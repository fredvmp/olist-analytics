import pandas as pd
import numpy as np
from app.utils.logger import logger
from app.repositories.sellers_repository import fetch_seller_scoring, fetch_category_hhi


def get_seller_scoring() -> pd.DataFrame:
    """
    Calcula el Seller Scoring integrando el volumen transaccional con métricas de calidad.
    Realiza un proceso de normalización de reseñas y puntualidad logística para generar 
    un "Quality Score" ponderado (70% satisfacción, 30% logística). 

    Posteriormente, aplica una segmentación por cuadrantes basada en la mediana de 
    ganancias y calidad del catálogo completo para clasificar a los vendedores.

    Returns:
        pd.DataFrame: DataFrame procesado con las siguientes columnas clave:
        - total_gains: Ingresos totales generados por el vendedor.
        - quality_score: Índice de calidad (0-100) basado en reseñas y cumplimiento de entrega.
        - seller_segment: Etiqueta de categoría (ej. "Top Seller" para alto volumen/alta 
          calidad o "At Risk" para alto volumen/baja calidad).
        - total_orders: Cantidad total de pedidos entregados.
    """

    logger.info("Executing sellers_service: get_seller_scoring")

    rows = fetch_seller_scoring()
    if not rows:
        return None

    df = pd.DataFrame(rows, columns=["seller_id", "seller_state", "seller_city",
                      "total_gains", "total_orders", "total_delayed_orders", "score_mean"])

    df["total_gains"] = pd.to_numeric(df["total_gains"])
    df["score_mean"] = pd.to_numeric(df["score_mean"])

    orders_on_time = df["total_orders"] - df["total_delayed_orders"]
    df["orders_on_time_perc"] = (orders_on_time / df["total_orders"]) * 100

    df["standardized_score"] = ((df["score_mean"] - 1) / (5 - 1)) * 100

    df["quality_score"] = (df["standardized_score"] * 0.7) + \
        (df["orders_on_time_perc"] * 0.3)

    df = df.fillna(0)

    median_gains = df["total_gains"].median()
    median_score = df["quality_score"].median()

    df["gains_tag"] = np.where(
        df["total_gains"] >= median_gains, "High", "Low")
    df["quality_tag"] = np.where(
        df["quality_score"] >= median_score, "High", "Low")

    conditions = [
        (df["quality_tag"] == "High") & (df["gains_tag"] == "High"),
        (df["quality_tag"] == "Low") & (df["gains_tag"] == "High"),
        (df["quality_tag"] == "High") & (df["gains_tag"] == "Low")
    ]
    labels = [
        "Top Seller (High quality, High gains)",
        "At Risk (Low quality, High gains)",
        "Promising (High quality, Low gains) "
    ]
    df["seller_segment"] = np.select(
        conditions, labels, default="Low Performer (Low quality, Low gains)")

    df = df.drop(columns=["gains_tag", "quality_tag",
                 "orders_on_time_perc", "standardized_score"])

    return df


def get_category_hhi() -> pd.DataFrame:
    """
    Calcula el Índice Herfindahl-Hirschman (HHI) para medir la competitividad por categoría.

    Procesa las ventas para obtener el Market Share (cuota de mercado) de cada vendedor, 
    eleva los porcentajes al cuadrado y los suma por categoría para obtener el índice HHI 
    (escala de 0 a 10.000). Finalmente, segmenta las categorías según los umbrales estándar 
    de concentración económica y las ordena por relevancia de ingresos.

    Returns:
        pd.DataFrame: DataFrame consolidado a nivel de categoría con las columnas:
        - category_name: Nombre de la categoría analizada.
        - category_revenue: Facturación global de la categoría.
        - hhi: Índice de concentración redondeado a entero.
        - market_type: Clasificación del entorno competitivo ("Competitivo", 
          "Moderadamente Concentrado" o "Altamente Concentrado").
    """

    logger.info("Executing sellers_service: get_category_hhi")

    rows = fetch_category_hhi()
    if not rows:
        return None

    df = pd.DataFrame(rows, columns=[
                      "seller_id", "category_name", "quantity_seller", "quantity_category"])

    df["quantity_seller"] = pd.to_numeric(df["quantity_seller"])
    df["quantity_category"] = pd.to_numeric(df["quantity_category"])

    df["market_share"] = (df["quantity_seller"] /
                          df["quantity_category"]) * 100

    df["share_squared"] = df["market_share"] ** 2

    hhi_df = df.groupby("category_name").agg(
        category_revenue=("quantity_category", "first"),
        hhi=("share_squared", "sum")
    ).reset_index()

    hhi_df["hhi"] = hhi_df["hhi"].round().astype(int)

    conditions = [
        # Mercado competitivo / Diversificado
        hhi_df["hhi"] < 1500,
        (hhi_df["hhi"] >= 1500) & (hhi_df["hhi"]
                                   < 2500),   # Concentración moderada
        # Alta concentración (Monopolio)
        hhi_df["hhi"] >= 2500
    ]
    choices = ["Competitivo", "Moderadamente Concentrado",
               "Altamente Concentrado"]

    hhi_df["market_type"] = np.select(
        conditions, choices, default="Desconocido")

    hhi_df = hhi_df.sort_values(
        by="category_revenue", ascending=False).reset_index(drop=True)

    return hhi_df

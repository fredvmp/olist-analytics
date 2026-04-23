import pandas as pd
import numpy as np
from app.utils.logger import logger
from app.repositories.customers_repository import fetch_customers_rfm, fetch_repurchase_retention


def get_customers_rfm() -> pd.DataFrame:
    """
    Procesa la segmentación de clientes mediante el modelo RFM.

    Transforma las métricas brutas en puntuaciones (1-5) usando quintiles y aplica 
    un motor de reglas basado en expresiones regulares para clasificar a los 
    clientes en segmentos de valor (Champions, Loyal, At Risk, etc.).

    Returns:
        pd.DataFrame | None: DataFrame procesado con las puntuaciones y el segmento final.
    """

    logger.info("Executing customer_service: get_customers_rfm")

    rows = fetch_customers_rfm()
    if not rows:
        return None

    df = pd.DataFrame(
        rows, columns=["customer_id", "recency", "frequency", "monetary"])

    df["recency"] = pd.to_numeric(df["recency"])
    df["monetary"] = pd.to_numeric(df["monetary"])
    df["frequency"] = pd.to_numeric(df["frequency"])

    # Cálculo de quintiles para cada métrica. Recency es inversa (menos días es mejor score)
    df["r"] = pd.qcut(df["recency"], q=5, labels=[
                      5, 4, 3, 2, 1], duplicates="drop")
    df["f"] = pd.qcut(df["frequency"], q=5, labels=False,
                      duplicates="drop") + 1
    df["m"] = pd.qcut(df["monetary"], q=5, labels=False, duplicates="drop") + 1

    # Concatenado 'RFM' para facilitar el filtrado
    df["rfm"] = df["r"].astype(str) + df["f"].astype(str) + df["m"].astype(str)

    """
    segment_map = {
        r"^[4-5][4-5][4-5]$": "Champions",
        r"^[4-5][2-5].$": "Loyal Customers",
        r"^[4-5]1.$": "New Customers",
        r"^[3-4][3-4][3-4]$": "Potential Loyalists",
        r"^[1-2][4-5][4-5]$": "At risk",
        r"^[1-2][4-5].$": "Can't Lose Them",
        r"^[1-2][1-2].$": "Hibernating",
    }

    df["segment"] = df["rfm"].replace(segment_map, regex=True)
    """

    # Segmentación basada en patrones del código RFM
    conditions = [
        df["rfm"].str.contains(r"^[4-5][4-5][4-5]$"),
        df["rfm"].str.contains(r"^[4-5][2-5].$"),
        df["rfm"].str.contains(r"^[4-5]1.$"),
        df["rfm"].str.contains(r"^[3-4][3-4][3-4]$"),
        df["rfm"].str.contains(r"^[1-2][4-5][4-5]$"),
        df["rfm"].str.contains(r"^[1-2][4-5].$"),
        df["rfm"].str.contains(r"^[1-2][1-2].$")
    ]
    # Etiquetas
    choices = [
        "Champions", "Loyal Customers", "New Customers", "Potential Loyalists", "At Risk", "Can't Lose Them", "Hibernating"
    ]

    # Aplicación de segmentos y formateo final de scores
    df["segment"] = np.select(
        conditions, choices, default="Standard Customers")
    df[["r", "f", "m"]] = df[["r", "f", "m"]].astype(int)

    return df


def get_repurchase_retention() -> pd.DataFrame:
    """
    Procesa los datos crudos de recompra y aplica las reglas de negocio para el análisis de retención.
    Transforma la información en un DataFrame, asegura los tipos de datos correctos y clasificar la 
    velocidad a la que regresan los usuarios. Además, evalúa la lealtad cruzando las categorías de entrada 
    y retorno.

    Returns:
        pd.DataFrame: Un DataFrame con las métricas de comportamiento. Sus columnas son:
        - customer_id: Identificador único del usuario.
        - first_purchase / second_purchase: Fechas exactas de la primera y segunda transacción.
        - first_category / second_category: Categoría del producto que enganchó al cliente la primera vez, 
          y la categoría a la que saltó (o repitió) en su regreso.
        - days_between_orders: Días transcurridos entre ambas compras.
        - repurchase_speed_range: Categoría de la velocidad de retorno.
        - is_same_category: Booleano que indica si el cliente compró en la misma categoría.
        - loyalty_type: Etiqueta descriptiva ("Same Category" o "Different Category") para analizar 
          la fidelidad al tipo de producto frente a la marca general.
    """

    rows = fetch_repurchase_retention()

    df = pd.DataFrame(rows, columns=["customer_id", "first_purchase", "first_category",
                      "second_purchase", "second_category", "days_between_orders"])

    df["days_between_orders"] = pd.to_numeric(df["days_between_orders"])
    df["first_purchase"] = pd.to_datetime(df["first_purchase"])
    df["second_purchase"] = pd.to_datetime(df["second_purchase"])

    """df_summary = df.groupby("first_category")["days_between_orders"].agg(
        cat_count="count",
        days_mean="mean",
        days_median="median"
    ).reset_index()

    df_summary["cat_percent"] = df_summary["cat_count"] / \
        df["customer_id"].count()"""

    """df_matrix = pd.crosstab(
        df["first_category"], 
        df["second_category"], 
        normalize='index'
    )"""

    bins = [0, 30, 90, 180, 365, float('inf')]
    labels = ["0-30 days", "30-90 days",
              "90-180 days", "180-365 days", "+1 year"]
    df["repurchase_speed_range"] = pd.cut(
        df["days_between_orders"], bins=bins, labels=labels)

    df["is_same_category"] = df["first_category"] == df["second_category"]
    df["loyalty_type"] = df["is_same_category"].map({
        True: "Same Category",
        False: "Different Category"
    })

    df = df.replace({np.nan: None})

    return df

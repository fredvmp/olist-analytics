import pandas as pd
import numpy as np
from app.utils.logger import logger
from app.repositories.product_repository import fetch_product_abc, fetch_category_abc


def get_product_abc() -> pd.DataFrame:
    """
    Calcula la clasificación ABC (Pareto) basándose en el ingreso acumulado.

    Ordena los productos de mayor a menor venta y les asigna una etiqueta:
    - "A": Generan el 80% del dinero (Productos estrella).
    - "B": Generan el siguiente 15% (Soporte).
    - "C": Generan el último 5% (baja rotación).

    Returns:
        pd.DataFrame: Tabla con ingresos, % acumulado y su etiqueta ABC.
    """
    logger.info("Executing product_service: get_product_abc")

    rows = fetch_product_abc()
    if not rows:
        return None

    df = pd.DataFrame(
        rows, columns=["product_id", "total_revenue", "category"])

    df["total_revenue"] = pd.to_numeric(df["total_revenue"])
    df = df.sort_values(by="total_revenue", ascending=False)

    # Cálculo del ingreso acumulado
    df["cumulative_revenue"] = df["total_revenue"].cumsum()

    # Cálculo del porcentaje sobre el total de ventas
    total_sales = df["total_revenue"].sum()
    df["percentage"] = df["cumulative_revenue"] / total_sales

    # Categorización -> A (80%), B (95%) y C (100%)
    conditions = [
        df["percentage"] <= 0.80,
        df["percentage"] <= 0.95,
        df["percentage"] <= 1.0,
    ]
    choices = ["A", "B", "C"]
    df["label"] = np.select(conditions, choices, default="Unknown")

    return df


def get_category_abc() -> pd.DataFrame:
    """
    Aplica la metodología ABC (Pareto) a las categorías.

    Calcula el peso relativo de cada categoría sobre el ingreso total, las ordena de 
    forma descendente y asigna etiquetas basadas en el aporte acumulado:
    - "A": Generan el 80% del dinero (Categorías estrella).
    - "B": Generan el siguiente 15% (Soporte).
    - "C": Generan el último 5% (baja rotación).

    Returns:
        pd.DataFrame: DataFrame con métricas de ingreso acumulado, porcentajes 
        y la clasificación ABC final por categoría.
    """

    logger.info("Executing product_service: get_category_abc")

    rows = fetch_category_abc()
    if not rows:
        return None

    df = pd.DataFrame(
        rows, columns=["rank", "category_name", "category_revenue"])

    df["category_revenue"] = pd.to_numeric(df["category_revenue"])
    df = df.sort_values(by="category_revenue",
                        ascending=False).reset_index(drop=True)
    df["cumulative_revenue"] = df["category_revenue"].cumsum()

    total_revenue = df["category_revenue"].sum()
    df["percentage"] = df["cumulative_revenue"] / total_revenue

    conditions = [
        df["percentage"] <= 0.80,
        df["percentage"] <= 0.95,
        df["percentage"] <= 1.0,
    ]
    choices = ["A", "B", "C"]
    df["label"] = np.select(conditions, choices, default="Unknown")

    return df

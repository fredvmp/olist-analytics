import pandas as pd
import numpy as np
from app.utils.logger import logger
from app.repositories.product_repository import fetch_product_abc


def get_product_abc() -> pd.DataFrame:
    """
    Calcula la clasificación ABC (Pareto) basándose en el ingreso acumulado.
    
    Ordena los productos de mayor a menor venta y les asigna una etiqueta:
    - 'A': Generan el 80% del dinero (Productos estrella).
    - 'B': Generan el siguiente 15% (Soporte).
    - 'C': Generan el último 5% (baja rotación).
    
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
    df = df.sort_values(by='total_revenue', ascending=False)

    df["cumulative_revenue"] = df["total_revenue"].cumsum()

    total_sales = df["total_revenue"].sum()
    df["percentage"] = df["cumulative_revenue"] / total_sales

    conditions = [
        df["percentage"] <= 0.80,
        df["percentage"] <= 0.95,
        df["percentage"] <= 1.0,
    ]
    choices = ["A", "B", "C"]
    df["label"] = np.select(conditions, choices, default="Unknown")

    return df

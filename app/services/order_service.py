import pandas as pd
import numpy as np
from app.utils.logger import logger
from app.repositories.order_repository import fetch_number_orders, fetch_user_retention


def get_number_orders():
    return fetch_number_orders()


def get_user_retention_percentage() -> pd.DataFrame:
    """
    Calcula la matriz de retención de usuarios en porcentajes.

    Mide qué parte de cada grupo de clientes (cohorte) vuelve a realizar 
    una compra en los meses siguientes a su primer pedido.

    Returns
    -------
    pd.DataFrame or None
        DataFrame con:
        - Index (cohort_month): El mes en que el cliente realizó su primera compra.
        - Columns (cohort_index): Meses transcurridos desde la primera compra (0, 1, 2...).
        - Values: Porcentaje de clientes que vuelven a comprar (de 0.0 a 1.0).
        Retorna None si no hay datos disponibles.
    """

    logger.info("Executing order_service: get_user_retention_percentage")

    rows = fetch_user_retention()
    if not rows:
        return None

    df = pd.DataFrame(rows, columns=[
        "customer_id", "purchase_month", "cohort_month"])

    df["purchase_month"] = pd.to_datetime(df["purchase_month"]).dt.to_period("M")
    df["cohort_month"] = pd.to_datetime(df["cohort_month"]).dt.to_period("M")

    df["cohort_index"] = (df["purchase_month"] - df["cohort_month"]).apply(lambda x: x.n)

    pivot = df.pivot_table(
        index="cohort_month",
        columns="cohort_index",
        values="customer_id",
        aggfunc="nunique",
        fill_value=0
    )

    cohort_sizes = pivot.iloc[:, 0]
    retention_matrix = pivot.divide(cohort_sizes, axis=0).round(4)

    retention_matrix.index = retention_matrix.index.astype(str)
    retention_matrix.columns = retention_matrix.columns.astype(str)

    return retention_matrix



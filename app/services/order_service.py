import pandas as pd
import numpy as np
from app.utils.logger import logger
from app.repositories.order_repository import fetch_number_orders, fetch_user_retention, fetch_logistics_sla


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

    df["purchase_month"] = pd.to_datetime(
        df["purchase_month"]).dt.to_period("M")
    df["cohort_month"] = pd.to_datetime(df["cohort_month"]).dt.to_period("M")

    # Cálculo de meses transcurridos desde la primera compra
    df["cohort_index"] = (df["purchase_month"] -
                          df["cohort_month"]).apply(lambda x: x.n)

    # Pivot table con los clientes únicos por mes de cohorte e índice
    pivot = df.pivot_table(
        index="cohort_month",
        columns="cohort_index",
        values="customer_id",
        aggfunc="nunique",
        fill_value=0
    )

    # Cálculo del porcentaje de retención dividiendo cada mes entre el tamaño inicial (mes 0)
    cohort_sizes = pivot.iloc[:, 0]
    retention_matrix = pivot.divide(cohort_sizes, axis=0).round(4)

    retention_matrix.index = retention_matrix.index.astype(str)
    retention_matrix.columns = retention_matrix.columns.astype(str)

    return retention_matrix


def get_logistics_sla() -> pd.DataFrame:
    """
    Transforma los datos crudos de logística en métricas de días y estados.

    Calcula:
    - sla_delta_days: Diferencia entre entrega real y estimada.
    - prep_time_days: Tiempo de preparación del vendedor.
    - transit_time_days: Tiempo en manos del transportista.
    - sla_status: Clasificación según el tiempo de entrega (Late, Early, On-Time).

    Returns:
        pd.DataFrame: DataFrame procesado para Power BI.
    """

    rows = fetch_logistics_sla()

    df = pd.DataFrame(rows, columns=["order_id", "purchase_timestamp", "delivered_carrier_date",
                      "delivered_customer_date", "estimated_delivery_date", "customer_state", "seller_state"])

    # Conversión de columnas de fecha a objetos datetime
    for col in ["purchase_timestamp", "delivered_carrier_date",
                "delivered_customer_date", "estimated_delivery_date"]:
        df[col] = pd.to_datetime(df[col])

    # Cálculo de KPIs temporales (Diferencia vs Estimado, Preparación y Tránsito)
    df["sla_delta_days"] = (
        df["delivered_customer_date"] - df["estimated_delivery_date"]).dt.days
    df["prep_time_days"] = (df["delivered_carrier_date"] -
                            df["purchase_timestamp"]).dt.days
    df["transit_time_days"] = (
        df["delivered_customer_date"] - df["delivered_carrier_date"]).dt.days

    # df["sla_status"] = np.where(df["sla_delta_days"] > 0, "Late", "On-Time")

    # Clasificación del estado de entrega según el cumplimiento de la fecha estimada
    conditions = [
        df["sla_delta_days"] > 0,   # Entregado después de la fecha estimada
        df["sla_delta_days"] < 0,   # Entregado antes de la fecha estimada
        df["sla_delta_days"] == 0   # Entregado el día exacto
    ]
    choices = ["Late", "Early", "On-Time"]
    df["sla_status"] = np.select(conditions, choices, default="Unknown")

    # Asegurar que no existan días negativos por errores en data de origen
    df["prep_time_days"] = df["prep_time_days"].clip(lower=0)
    df["transit_time_days"] = df["transit_time_days"].clip(lower=0)

    # Limpieza del DataFrame final
    df = df.drop(columns=["delivered_carrier_date",
                 "delivered_customer_date", "estimated_delivery_date"])

    return df

from app.utils.database import get_db_cursor
from app.utils.logger import logger
from typing import List, Tuple


def fetch_number_orders() -> int:
    """
    Consulta la base de datos para obtener el número total de pedidos.

    Returns:
        int: Número total de registros en la tabla "orders".
    """

    logger.info("Executing query: fetch_number_orders")

    query = """
        SELECT COUNT(*) 
        FROM orders
    """

    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()[0]


def fetch_user_retention() -> List[Tuple]:
    """
    Extrae la actividad mensual de compra de los usuarios únicos.

    Esta consulta utiliza Window Functions para identificar el mes de la 
    primera compra (el cohorte) de cada cliente y lo cruza con sus compras 
    posteriores. Solo para pedidos entregados ('delivered').

    Returns:
        List[Tuple]: Una lista de tuplas con el formato:
            (customer_id, purchase_month, cohort_month).
            - purchase_month y cohort_month son objetos datetime truncados al mes.
    """

    logger.info("Executing query: fetch_user_retention")

    query = """
        WITH detailed_purchases AS (
            SELECT
                c.customer_unique_id AS customer_id,
                DATE_TRUNC('month', o.order_purchase_timestamp) AS purchase_month,
                MIN(DATE_TRUNC('month', o.order_purchase_timestamp)) OVER (PARTITION BY c.customer_unique_id) AS cohort_month
            FROM customers c
            JOIN orders o ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
        ) 
        SELECT DISTINCT
            customer_id, 
            purchase_month, 
            cohort_month
        FROM detailed_purchases
        ORDER BY customer_id, purchase_month
    """

    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

from app.utils.database import get_db_cursor
from app.utils.logger import logger
from typing import List, Tuple


def fetch_customers_rfm() -> List[Tuple]:
    """
    Extrae las métricas base (RFM) por cliente desde la base de datos.

    Calcula la recencia (días desde la última compra), la frecuencia (pedidos únicos) 
    y el valor monetario (gasto total) de cada cliente, tomando como referencia 
    la fecha de la última transacción registrada en el sistema.

    Returns:
        List[Tuple] | None: Lista de registros con el siguiente esquema:
            (customer_id, recency, frequency, monetary).
            - customer_unique_id (str): Identificador único del cliente.
            - recency (int): Días transcurridos hasta la fecha máxima del dataset.
            - frequency (int): Cantidad de pedidos distintos con estado 'delivered'.
            - monetary (float): Suma total del valor de todos los pagos realizados.
    """

    logger.info("Executing query: fetch_customers_rfm")

    query = """
        WITH purchases AS (
            SELECT MAX(order_purchase_timestamp) AS last_date_db 
            FROM orders 
        )
        SELECT DISTINCT
            c.customer_unique_id AS customer_id, 
            EXTRACT(DAY FROM (p.last_date_db - MAX(o.order_purchase_timestamp))) AS recency,
            COUNT(o.order_id) AS frequency,
            SUM(op.payment_value) AS monetary
        FROM customers c CROSS JOIN purchases p
        JOIN orders o ON o.customer_id = c.customer_id
        JOIN order_payments op ON op.order_id = o.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id, p.last_date_db
    """

    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

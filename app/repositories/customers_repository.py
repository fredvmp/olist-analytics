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


def fetch_repurchase_retention() -> List[Tuple]:
    """
    Consulta en la base de datos el historial de transacciones para extraer el viaje entre la 
    primera y segunda compra de los usuarios recurrentes. Utiliza CTEs y 
    Window Functions para ordenar cronológicamente los pedidos, alinear las categorías compradas 
    y calcular el tiempo exacto de retención, excluyendo compras simultáneas o errores 
    (menos de 1 hora de diferencia).

    Returns:
        List[Tuple]: Una lista de tuplas con los datos en bruto extraídos de la base de datos. 
        Cada tupla representa:
        - customer_unique_id (str): Identificador único del comprador.
        - first_purchase (datetime): Timestamp del primer pedido.
        - first_category (str): Nombre de la categoría principal del primer pedido.
        - second_purchase (datetime): Timestamp del pedido en el que regresó.
        - second_category (str): Nombre de la categoría principal de su pedido de regreso.
        - days_between_orders (int): Días exactos transcurridos entre ambos eventos.
    """

    query = """
        WITH products_categories_1 AS (
            SELECT 
                c.customer_unique_id,
                o.order_id,
                MAX(pcnt.product_category_name_english) AS category,
                o.order_purchase_timestamp
            FROM customers c
            JOIN orders o ON o.customer_id = c.customer_id
            JOIN order_items oi ON oi.order_id = o.order_id
            JOIN products p ON p.product_id = oi.product_id
            JOIN product_category_name_translation pcnt ON pcnt.product_category_name = p.product_category_name
            GROUP BY c.customer_unique_id, o.order_id, o.order_purchase_timestamp
        ),
        products_categories_2 AS (
            SELECT 	
                customer_unique_id,
                order_id,
                category,
                order_purchase_timestamp AS first_purchase,
                LEAD(category) OVER (
                    PARTITION BY customer_unique_id 
                    ORDER BY order_purchase_timestamp ASC
                ) AS second_category,
                LEAD(order_purchase_timestamp) OVER (
                    PARTITION BY customer_unique_id 
                    ORDER BY order_purchase_timestamp ASC
                ) AS second_purchase,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_unique_id
                    ORDER BY order_purchase_timestamp ASC
                ) AS n
            FROM products_categories_1 
        )
        SELECT 
            customer_unique_id,
            first_purchase,
            category AS first_category,
            second_purchase,
            second_category,
            EXTRACT(DAY FROM (second_purchase - first_purchase)) AS days_between_orders
        FROM products_categories_2
        WHERE n = 1 
            AND second_purchase IS NOT NULL
            AND (second_purchase - first_purchase) > INTERVAL '1 hour'
    """

    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

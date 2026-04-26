from app.utils.database import get_db_cursor
from app.utils.logger import logger
from typing import List, Tuple


def fetch_seller_scoring() -> List[Tuple]:
    """
    Ejecuta una consulta avanzada en la base de datos para consolidar el histórico de 
    operaciones de los vendedores. Utiliza CTEs para procesar a nivel de orden el 
    ingreso por venta, la calificación del cliente y los retrasos logísticos.

    Filtra únicamente las órdenes con estado 'delivered' para asegurar que el análisis 
    se base en experiencias de cliente completadas.

    Returns:
        List[Tuple]: Lista de registros agrupados por vendedor con los campos:
        - seller_id, seller_state, seller_city: Datos de identificación y ubicación.
        - total_gains: Sumatorio de los precios de los artículos vendidos.
        - total_orders: Conteo total de órdenes únicas.
        - total_delayed_orders: Cantidad de órdenes entregadas después de la fecha estimada.
        - score_mean: Promedio de las calificaciones recibidas en las reseñas.
    """

    query = """
        WITH seller_summary AS (
            SELECT 
                s.seller_id,
                o.order_id,
                s.seller_state,
                s.seller_city,
                SUM(oi.price) AS revenue_per_order,
                MAX(ors.review_score) AS score_per_order,
                CASE 
                    WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 
                    ELSE 0 
                END AS is_delayed
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN order_reviews ors ON o.order_id = ors.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY 
                s.seller_id, 
                o.order_id, 
                s.seller_state, 
                s.seller_city, 
                o.order_delivered_customer_date, 
                o.order_estimated_delivery_date
        )
        SELECT 
            seller_id,
            seller_state,
            seller_city,
            SUM(revenue_per_order) AS total_gains,
            COUNT(order_id) AS total_orders,
            SUM(is_delayed) AS total_delayed_orders,
            AVG(score_per_order) AS score_mean
        FROM seller_summary
        GROUP BY seller_id, seller_state, seller_city
    """

    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

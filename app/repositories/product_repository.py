from app.utils.database import get_db_cursor
from app.utils.logger import logger
from typing import List, Tuple


def fetch_product_abc() -> List[Tuple]:
    """
    Consulta en la base de datos el ingreso total por cada producto vendido.
    
    Une las tablas de pedidos y productos para sumar ventas (solo 'delivered') y traduce 
    las categorías al inglés. Si un producto no tiene categoría, lo marca como 'unknown'.
    
    Returns:
        List[Tuple]: Lista con (product_id, total_revenue, category).
    """

    query = """
        SELECT 
            oi.product_id,
            SUM(oi.price) AS total_revenue,
            COALESCE(pcnt.product_category_name_english, 'unknown') AS category
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        LEFT JOIN products p ON p.product_id = oi.product_id
        LEFT JOIN product_category_name_translation pcnt ON pcnt.product_category_name = p.product_category_name
        WHERE o.order_status = 'delivered'
        GROUP BY oi.product_id, pcnt.product_category_name_english
    """

    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

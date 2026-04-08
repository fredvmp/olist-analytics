from app.utils.database import get_db_cursor
from app.utils.logger import logger


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

import psycopg2
from contextlib import contextmanager
from config import Config
from app.utils.logger import logger


def get_connection():
    """
    Establece la conexión física con la base de datos PostgreSQL.
    """
    try:
        # Intento de conexión usando las credenciales cargadas en Config
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            sslmode="require"
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise e


@contextmanager
def get_db_cursor():
    """
    Context Manager para asegurar el cierre de conexiones y manejo de transacciones.
    """
    conn = None
    cursor = None
    try:
        # Inicialización de conexión y cursor para ejecutar queries
        conn = get_connection()
        cursor = conn.cursor()
        yield cursor # Entrega el cursor al bloque "with" que lo invoque

        # Si todo sale bien, se confirman los cambios en la DB
        conn.commit() 
    except Exception as e:
        if conn:
            # Si hay error en la query, se deshacen los cambios para evitar datos corruptos
            conn.rollback()
        logger.error(f"Database error in Context Manager: {e}")
        raise e
    finally:
        # Cerrar cursor y conexión 
        if cursor:
            cursor.close()
        if conn:
            conn.close()

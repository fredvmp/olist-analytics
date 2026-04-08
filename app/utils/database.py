import psycopg2
from contextlib import contextmanager
from config import Config
from app.utils.logger import logger

def get_connection():
    try:
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
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in Context Manager: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
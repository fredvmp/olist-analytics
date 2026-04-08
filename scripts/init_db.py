from app.utils.database import get_db_cursor
from app.utils.logger import logger
import os

def initialize_database():
    schema_path = os.path.join('database', 'schema.sql')
    
    if not os.path.exists(schema_path):
        logger.error("The schema.sql file was not found in /database")
        return

    try:
        with open(schema_path, 'r') as f:
            sql_script = f.read()

        with get_db_cursor() as cur:
            logger.info("Running the table creation script...")
            cur.execute(sql_script)
            logger.info("Database initialized successfully.")
            
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")

if __name__ == "__main__":
    initialize_database()
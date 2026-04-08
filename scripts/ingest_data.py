import pandas as pd
import numpy as np
from psycopg2.extras import execute_values
from app.utils.database import get_db_cursor
from app.utils.logger import logger
import os

# Diccionario de configuración: {Nombre_Tabla: Nombre_Archivo_CSV}
# Ordenado por Foreign Keys
TABLES_TO_INGEST = {
    "product_category_name_translation": "product_category_name_translation.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv"
}


def clean_dataframe(df, table_name):
    # Limpieza de fechas
    date_columns = [
        col for col in df.columns if 'timestamp' in col or 'date' in col]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Rellenamos nulos en category - products
    if table_name == "products":
        if 'product_category_name' in df.columns:
            df['product_category_name'] = df['product_category_name'].fillna(
                'unknown')
            logger.info(
                "Transformation: Nulls in 'product_category_name' turned into 'unknown'")

        # Forzar a que sean numéricos
        numeric_cols = ['product_name_lenght', 'product_description_lenght', 'product_photos_qty',
                        'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']

        for col in numeric_cols:
            if col in df.columns:  # Solo si la columna existe en este CSV
                df[col] = pd.to_numeric(df[col], errors='coerce')

    # Manejo de Nulos general (convertir NaN de Pandas a None de Python/SQL)
    df = df.replace({pd.NaT: None, np.nan: None})
    return df.where(pd.notnull(df), None)


def ingest_table(table_name, file_name):
    file_path = os.path.join('data', 'raw', file_name)

    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}. Skipping...")
        return

    logger.info(f"Starting with: {table_name}")

    # Extraer
    df = pd.read_csv(file_path)

    # Transformar
    df = clean_dataframe(df, table_name)

    # Cargar
    columns = ",".join(df.columns)
    query = f"INSERT INTO {table_name} ({columns}) VALUES %s ON CONFLICT DO NOTHING"

    data_tuples = [tuple(x) for x in df.to_numpy()]

    try:
        with get_db_cursor() as cur:              # Para enviar los datos en bloques pequeños
            execute_values(cur, query, data_tuples, page_size=10000)
            logger.info(
                f"Success: {len(df)} records processed in {table_name}")
    except Exception as e:
        logger.error(f"DATABASE ERROR IN {table_name}: {e}")
        raise e  # Lanzamos el error para que run_pipeline lo capture y libere la conexión bloqueada


def run_pipeline():
    for table, file in TABLES_TO_INGEST.items():
        try:
            ingest_table(table, file)
        except Exception as e:
            logger.error(f"FAILURE IN {table}: {e}")


if __name__ == "__main__":
    run_pipeline()

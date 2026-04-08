import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    # Crear carpeta de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger("olist_logger")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo (rota cada 5MB, guarda los últimos 5 archivos)
    file_handler = RotatingFileHandler('logs/olist.log', maxBytes=5242880, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Instancia única
logger = setup_logger()
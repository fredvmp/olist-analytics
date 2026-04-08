from app.utils.logger import logger
from app.repositories.order_repository import fetch_number_orders


def get_number_orders():
    return fetch_number_orders()

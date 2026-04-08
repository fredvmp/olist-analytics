from flask import Blueprint, jsonify
from app.utils.logger import logger
from app.services.order_service import get_number_orders


orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("/number-orders", methods=["GET"])
def number_orders():
    """
    Obtiene el número total de pedidos de Olist.

    Endpoint de prueba para verificar la conexión con la base de datos 
    y la integridad del flujo de datos.

    Returns:
        JSON: { "total_orders": int } y Status 200 si tiene éxito.
        JSON: { "message": str } y Status 500 si hay error de base de datos.
    """

    logger.info("GET /orders/number-orders requested")
    result = get_number_orders()
    if result is None:
        return jsonify({"message": "Error fetching data"}), 500
    return jsonify({"total_orders": result}), 200

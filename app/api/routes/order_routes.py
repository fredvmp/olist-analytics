from flask import Blueprint, jsonify, Response
from app.utils.logger import logger
from app.services.order_service import get_number_orders, get_user_retention_percentage


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


@orders_bp.route("/user-retention", methods=["GET"])
def user_retention() -> Response:
    """
    Obtiene la matriz de retención de usuarios basada en cohortes mensuales.

    Calcula el porcentaje de usuarios que vuelven a realizar una compra en los meses posteriores 
    a su primera compra. Los datos se devuelven en formato de registros (orientados a filas) 
    para facilitar su consumo en Power BI.

    Returns:
        Response: Objeto JSON que contiene una lista de diccionarios con:
            - cohort_month (str): Mes de inicio de la cohorte (YYYY-MM).
            - [month_index] (float): Columnas que contienen el porcentaje de 
            retención (0.0 a 1.0) para cada mes transcurrido desde la primera compra (0, 1, 2...).
    Raises:
        500: Si ocurre un error al procesar los datos o no hay registros.
    """

    logger.info("GET /orders/user-retention")
    result = get_user_retention_percentage()
    if result is None:
        return jsonify({"message": "Error fetching data"}), 500
    return jsonify(result.reset_index().to_dict(orient='records'))




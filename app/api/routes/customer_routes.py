from flask import Blueprint, jsonify, Response
from app.utils.logger import logger
from app.services.customers_service import get_customers_rfm, get_repurchase_retention


customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


@customers_bp.route("/customers-rfm", methods=["GET"])
def customers_rfm() -> Response:
    """
    Endpoint para obtener la segmentación RFM de los clientes.

    Expone los datos en formato de registros (orientado a filas) para facilitar 
    su integración con Power BI.

    Returns:
        JSON: Lista de objetos cliente con métricas, scores y segmento asignado.
        500: Si no se encuentran datos o hay un error en el servidor.
    """

    logger.info("GET /customers/rfm")
    result = get_customers_rfm()
    if result is None:
        return jsonify({"message": "Error fetching data"}), 500
    return jsonify(result.reset_index().to_dict(orient="records")), 200


@customers_bp.route("/repurchase-retention", methods=["GET"])
def repurchase_retention() -> Response:
    """
    Endpoint para obtener el análisis de retención y comportamiento de recompra de los clientes. 
    Llama al servicio de procesamiento y sirve los datos finales en formato JSON, listos para 
    ser consumidos por Power BI.

    Returns:
        Response: Un objeto de respuesta HTTP. 
        - En caso de éxito (200 OK), devuelve un JSON con una lista de diccionarios (orient='records') 
          que incluye el perfil de recompra de cada cliente (tiempos, categorías y rangos de velocidad).
        - En caso de fallo (500 Internal Server Error), devuelve un JSON con un mensaje de error.
    """

    logger.info("GET /repurchase-retention")
    result = get_repurchase_retention()
    if result is None:
        return jsonify({"message": "Error fetching data"}), 500
    return jsonify(result.reset_index().to_dict(orient="records")), 200


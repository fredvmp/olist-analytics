from flask import Blueprint, jsonify, Response
from app.utils.logger import logger
from app.services.sellers_service import get_seller_scoring


seller_bp = Blueprint("sellers", __name__, url_prefix="/sellers")


@seller_bp.route("/seller-scoring", methods=["GET"])
def seller_scoring() -> Response:
    """
    Endpoint para obtener la matriz de performance y calidad de los vendedores. 
    Sirve los datos procesados en formato JSON para Power BI.

    Returns:
        Response: Objeto JSON que contiene una lista de registros con las métricas 
        consolidadas de cada vendedor, incluyendo su segmentación final (Top Seller, 
        At Risk, Promising o Low Performer) y sus indicadores de ingresos y calidad.
    """

    logger.info("GET /seller-scoring")
    result = get_seller_scoring()
    if result is None:
        return jsonify({"message": "Error fetching data"}), 500
    return jsonify(result.reset_index().to_dict(orient="records")), 200

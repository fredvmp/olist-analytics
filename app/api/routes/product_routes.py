from flask import Blueprint, jsonify, Response
from app.utils.logger import logger
from app.services.product_service import get_product_abc


products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("/product-abc", methods=["GET"])
def product_abc():
    """
    Endpoint para obtener el ranking de importancia de productos.

    Sirve los datos del análisis ABC en formato JSON para visualizaciones 
    de inventario y rentabilidad en el dashboard.
    """

    logger.info("GET /products/product-abc requested")
    result = get_product_abc()
    if result is None:
        return jsonify({"message": "Error fetching data"}), 500
    return jsonify(result.to_dict(orient='records'))

from flask import Flask
from config import Config
from app.utils.logger import logger
from app.api.errors import register_error_handlers
from app.api.routes.order_routes import orders_bp
from app.api.routes.customer_routes import customers_bp
from app.api.routes.product_routes import products_bp
from app.api.routes.sellers_routes import seller_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.json.ensure_ascii = False

    register_error_handlers(app)

    app.register_blueprint(orders_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(seller_bp)

    logger.info(
        f"Olist ecosystem launched in: {'Debug' if Config.DEBUG else 'Production'}")

    return app

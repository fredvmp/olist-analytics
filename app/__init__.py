from flask import Flask
from config import Config
from app.utils.logger import logger
from app.api.errors import register_error_handlers
from app.api.routes.order_routes import orders_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
        
    app.json.ensure_ascii = False

    register_error_handlers(app)
    
    app.register_blueprint(orders_bp)

    logger.info(f"Olist ecosystem launched in: {'Debug' if Config.DEBUG else 'Production'}")

    return app



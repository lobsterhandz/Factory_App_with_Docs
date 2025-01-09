from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, current_app
from flask_migrate import Migrate
from models import db
from config import DevelopmentConfig
from limiter import limiter
from flask_cors import CORS

# Add project root to sys.path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Add the queries folder explicitly
queries_path = os.path.join(project_root, 'queries')
sys.path.insert(0, queries_path)

print("Current Working Directory:", os.getcwd())
print("Python Path:", sys.path)

# Import blueprints
from blueprints.employee_blueprint import employee_bp
from blueprints.product_blueprint import product_bp
from blueprints.order_blueprint import order_bp
from blueprints.customer_blueprint import customer_bp
from blueprints.production_blueprint import production_bp
from blueprints.analytics_blueprint import analytics_bp
from blueprints.user_blueprint import user_bp  # Import user blueprint

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

def setup_logging(app):
    """
    Configures logging for the app. If in testing or production, it will handle log rotation.
    """
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # File logging configuration
    file_handler = logging.FileHandler('logs/factory_management.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    
    # Add console logging for testing or debugging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Factory Management System startup')

def create_app(config_class=DevelopmentConfig):
    """
    Factory method to create and configure the Flask application.

    Args:
        config_class: Configuration class to load settings.

    Returns:
        Flask: Configured Flask application instance.
    """
    # Create Flask app instance
    app = Flask(__name__)
    app.config.from_object(config_class)

    # CORS configuration
    CORS(app)  # Allow cross-origin requests for APIs

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)  # Database migration
    limiter.init_app(app)

    # Set up logging
    setup_logging(app)

    # ---------------------------
    # Rate Limiter Configuration
    # ---------------------------
    limiter.request_filter(lambda: request.remote_addr == '127.0.0.1')

    # ---------------------------
    # Register Blueprints
    # ---------------------------
    app.register_blueprint(employee_bp, url_prefix='/employees')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(production_bp, url_prefix='/production')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')  # Analytics routes
    app.register_blueprint(user_bp, url_prefix='/auth')  # User routes

    # ---------------------------
    # Routes and Error Handlers
    # ---------------------------
    @app.route('/')
    def index():
        """Default landing page."""
        return jsonify({"message": "Welcome to the Factory Management System!"}), 200

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy"}), 200

    # ---------------------------
    # Error Handlers
    # ---------------------------
    @app.errorhandler(404)
    def not_found(error):
        """Handles 404 errors."""
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handles 500 errors."""
        app.logger.error(f"Server error: {str(error)}")
        return jsonify({"error": "Internal Server Error"}), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handles rate limit errors."""
        return jsonify({"error": "Rate limit exceeded"}), 429

    return app


if __name__ == '__main__':
    # Load configuration from environment variable or use default
    config_class = os.getenv('FLASK_CONFIG', 'config.DevelopmentConfig')
    app = create_app(config_class=config_class)

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

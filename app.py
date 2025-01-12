from flask import Flask, jsonify, request
from flasgger import Swagger
from models import db
from config import config_by_name
from flask_migrate import Migrate
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

# Import blueprints
from blueprints.employee_blueprint import employee_bp
from blueprints.product_blueprint import product_bp
from blueprints.order_blueprint import order_bp
from blueprints.customer_blueprint import customer_bp
from blueprints.production_blueprint import production_bp
from blueprints.analytics_blueprint import analytics_bp
from blueprints.user_blueprint import user_bp


def create_app(config_name='development'):
    """
    Factory function to create and configure the Flask application.

    Args:
        config_name (str): Configuration name ('development', 'testing', 'production').

    Returns:
        Flask: Configured Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Enable CORS
    CORS(app)

    # Initialize database and migrations
    db.init_app(app)
    Migrate(app, db)

    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/swagger.json",
                "rule_filter": lambda rule: True,  # Include all routes
                "model_filter": lambda tag: True,  # Include all models
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
    }
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Factory Management System API",
            "description": "API documentation for managing employees, products, orders, and analytics.",
            "contact": {
                "name": "Support Team",
                "email": "support@example.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            },
            "version": "1.0.0"
        },
        "host": "127.0.0.1:5000",  # Update this for production environments
        "basePath": "/",
        "schemes": ["http"],  # Change to 'https' in production
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": (
                    "JWT Authorization header using the Bearer scheme. "
                    "Example: 'Authorization: Bearer {token}'"
                )
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Logging setup
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/factory_management.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Factory Management System startup')

    # Register blueprints
    app.register_blueprint(employee_bp, url_prefix='/employees')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(production_bp, url_prefix='/production')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(user_bp, url_prefix='/auth')

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy"}), 200

    # Route for debugging all registered routes
    @app.route('/routes', methods=['GET'])
    def list_routes():
        """Lists all routes in the application for debugging."""
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            output.append(f"{rule.endpoint}: {rule.rule} [{methods}]")
        return jsonify(output)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server error: {str(error)}")
        return jsonify({"error": "Internal Server Error"}), 500

    return app


if __name__ == '__main__':
    # Run the application
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app = create_app(config_name=config_name)
    app.run(debug=True, host='0.0.0.0', port=5000)

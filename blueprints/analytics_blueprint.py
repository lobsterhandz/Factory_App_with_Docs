from flask import Blueprint, request, jsonify
from queries.analytics_queries import (
    analyze_employee_performance,
    top_selling_products,
    customer_lifetime_value,
    evaluate_production_efficiency,
)
from flask_jwt_extended import jwt_required
from utils.utils import error_response, role_required
from limiter import limiter
from flask_caching import Cache
from flasgger.utils import swag_from
import logging

# Create Blueprint
analytics_bp = Blueprint('analytics', __name__)
cache = Cache()

# ---------------------------
# Route 1: Analyze Employee Performance
# ---------------------------
@analytics_bp.route('/employee-performance', methods=['GET'])
@cache.cached(query_string=True)  # Cache GET requests with query parameters
@jwt_required()  # Requires valid JWT
@role_required('admin')  # Requires admin role
@limiter.limit("10 per minute")  # Rate limiting
@swag_from({
    "tags": ["Analytics"],
    "summary": "Analyze employee performance",
    "description": "Calculates the total quantity of products produced by each employee.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Successfully retrieved employee performance data.",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "employee_name": {"type": "string"},
                                "total_quantity": {"type": "integer"},
                            },
                        },
                    },
                    "status": {"type": "string"},
                },
            },
        },
        "500": {"description": "Internal server error."},
    },
})
def employee_performance():
    """Analyze employee performance."""
    try:
        data = analyze_employee_performance()
        return jsonify({"data": data, "status": "success"}), 200
    except Exception as e:
        logging.error(f"Error analyzing employee performance: {str(e)}")
        return error_response(str(e), 500)

# ---------------------------
# Route 2: Top-Selling Products
# ---------------------------
@analytics_bp.route('/top-products', methods=['GET'])
@cache.cached(query_string=True)
@jwt_required()
@role_required('admin')
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Analytics"],
    "summary": "Retrieve top-selling products",
    "description": "Fetches the top-selling products based on total quantity ordered, sorted in descending order.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Successfully retrieved top-selling products.",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_name": {"type": "string"},
                                "total_quantity": {"type": "integer"},
                            },
                        },
                    },
                    "status": {"type": "string"},
                },
            },
        },
        "500": {"description": "Internal server error."},
    },
})
def top_products():
    """Retrieve top-selling products."""
    try:
        data = top_selling_products()
        return jsonify({"data": data, "status": "success"}), 200
    except Exception as e:
        logging.error(f"Error fetching top-selling products: {str(e)}")
        return error_response(str(e), 500)

# ---------------------------
# Route 3: Customer Lifetime Value
# ---------------------------
@analytics_bp.route('/customer-lifetime-value', methods=['GET'])
@cache.cached(query_string=True)
@jwt_required()
@role_required('admin')
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Analytics"],
    "summary": "Calculate customer lifetime value",
    "description": "Calculates the total value of orders placed by each customer, filtered by an optional threshold.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "threshold",
            "in": "query",
            "type": "number",
            "description": "Minimum total order value to filter customers (default: 1000).",
        }
    ],
    "responses": {
        "200": {
            "description": "Successfully calculated customer lifetime value.",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "customer_name": {"type": "string"},
                                "lifetime_value": {"type": "number"},
                            },
                        },
                    },
                    "status": {"type": "string"},
                },
            },
        },
        "400": {"description": "Validation error."},
        "500": {"description": "Internal server error."},
    },
})
def lifetime_value():
    """Calculate customer lifetime value."""
    try:
        threshold = request.args.get('threshold', default=1000, type=float)
        if threshold < 0:
            return error_response("Threshold must be a positive value.", 400)

        data = customer_lifetime_value(threshold=threshold)
        return jsonify({"data": data, "status": "success"}), 200
    except Exception as e:
        logging.error(f"Error calculating customer lifetime value: {str(e)}")
        return error_response(str(e), 500)

# ---------------------------
# Route 4: Evaluate Production Efficiency
# ---------------------------
@analytics_bp.route('/production-efficiency', methods=['GET'])
@cache.cached(query_string=True)
@jwt_required()
@role_required('admin')
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Analytics"],
    "summary": "Evaluate production efficiency",
    "description": "Calculates the total quantity produced for each product on a specific date.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "date",
            "in": "query",
            "type": "string",
            "required": True,
            "description": "Date in YYYY-MM-DD format.",
        }
    ],
    "responses": {
        "200": {
            "description": "Successfully evaluated production efficiency.",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_name": {"type": "string"},
                                "total_quantity": {"type": "integer"},
                            },
                        },
                    },
                    "status": {"type": "string"},
                },
            },
        },
        "400": {"description": "Validation error."},
        "500": {"description": "Internal server error."},
    },
})
def production_efficiency():
    """Evaluate production efficiency."""
    try:
        date = request.args.get('date')
        if not date:
            return error_response("Date is required (YYYY-MM-DD).", 400)

        data = evaluate_production_efficiency(date)
        return jsonify({"data": data, "status": "success"}), 200
    except Exception as e:
        logging.error(f"Error evaluating production efficiency: {str(e)}")
        return error_response(str(e), 500)

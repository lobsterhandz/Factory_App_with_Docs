from flask import Blueprint, request, jsonify
from queries.analytics_queries import (
    analyze_employee_performance,
    top_selling_products,
    customer_lifetime_value,
    evaluate_production_efficiency
)
from utils.utils import error_response, role_required
from limiter import limiter
import logging

# Create Blueprint
analytics_bp = Blueprint('analytics', __name__)


# ---------------------------
# Route 1: Analyze Employee Performance
# ---------------------------
@analytics_bp.route('/employee-performance', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Requires admin or higher role
def employee_performance():
    """
    Analyze employee performance by calculating the total quantity of products each employee has produced.

    Returns:
        JSON response with aggregated data grouped by employee name.
    """
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
@limiter.limit("10 per minute")
@role_required('admin')  # Requires admin or higher role
def top_products():
    """
    Fetch top-selling products based on total quantity ordered.

    Returns:
        JSON response sorted by total quantity in descending order.
    """
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
@limiter.limit("10 per minute")
@role_required('admin')  # Requires admin or higher role
def lifetime_value():
    """
    Calculate the total value of orders placed by each customer.
    
    Query Parameters:
        - threshold (float): Minimum total order value to filter customers (default: 1000).

    Returns:
        JSON response filtered by threshold.
    """
    try:
        # Validate threshold input
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
@limiter.limit("10 per minute")
@role_required('admin')  # Requires admin or higher role
def production_efficiency():
    """
    Evaluate production efficiency by calculating the total quantity produced for each product on a specific date.

    Query Parameters:
        - date (str): Date in YYYY-MM-DD format (required).

    Returns:
        JSON response grouped by product name.
    """
    try:
        # Validate and parse date input
        date = request.args.get('date', default=None, type=str)
        if not date:
            return error_response("Date is required (YYYY-MM-DD).", 400)

        data = evaluate_production_efficiency(date)
        return jsonify({"data": data, "status": "success"}), 200
    except Exception as e:
        logging.error(f"Error evaluating production efficiency: {str(e)}")
        return error_response(str(e), 500)

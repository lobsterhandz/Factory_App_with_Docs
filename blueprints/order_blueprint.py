from flask import Blueprint, request, jsonify
from services.order_service import OrderService
from schemas.order_schema import order_schema, orders_schema
from utils.utils import error_response, role_required, jwt_required
from limiter import limiter
from flask_caching import Cache
from flasgger.utils import swag_from

# Create Blueprint
order_bp = Blueprint('orders', __name__)
cache = Cache()  # Add caching instance

# Allowed sortable fields
SORTABLE_FIELDS = ['created_at', 'quantity', 'total_price']


# ---------------------------
# Create an Order
# ---------------------------
@order_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting
@jwt_required  # Requires valid JWT token
@role_required('user')  # Restrict to 'user' role
@swag_from({
    "tags": ["Orders"],
    "summary": "Create a new order",
    "description": "Creates a new order with the specified details.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["customer_id", "product_id", "quantity"],
                "properties": {
                    "customer_id": {"type": "integer", "description": "ID of the customer placing the order."},
                    "product_id": {"type": "integer", "description": "ID of the product being ordered."},
                    "quantity": {"type": "integer", "description": "Quantity of the product ordered."}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "Order created successfully."},
        "400": {"description": "Validation or creation error."},
        "500": {"description": "Internal server error."}
    }
})
def create_order():
    """
    Creates a new order.
    """
    try:
        data = request.get_json()
        validated_data = order_schema.load(data)
        order = OrderService.create_order(**validated_data)
        return jsonify(order_schema.dump(order)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Orders
# ---------------------------
@order_bp.route('', methods=['GET'])
@cache.cached(query_string=True)  # Cache GET requests with query parameters
@limiter.limit("10 per minute")  # Rate limiting
@jwt_required  # Requires valid JWT token
@role_required('admin')  # Admin-only access
@swag_from({
    "tags": ["Orders"],
    "summary": "Retrieve paginated orders",
    "description": "Retrieves paginated orders with optional sorting and metadata.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "description": "Page number (default: 1)."},
        {"name": "per_page", "in": "query", "type": "integer", "description": "Records per page (default: 10)."},
        {"name": "sort_by", "in": "query", "type": "string", "description": "Field to sort by (default: 'created_at')."},
        {"name": "sort_order", "in": "query", "type": "string", "description": "Sorting order ('asc' or 'desc')."},
        {"name": "include_meta", "in": "query", "type": "boolean", "description": "Include metadata (default: true)."}
    ],
    "responses": {
        "200": {
            "description": "Successfully retrieved paginated orders.",
            "schema": {
                "type": "object",
                "properties": {
                    "orders": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Order"}
                    },
                    "total": {"type": "integer"},
                    "pages": {"type": "integer"},
                    "page": {"type": "integer"},
                    "per_page": {"type": "integer"}
                }
            }
        },
        "500": {"description": "Internal server error."}
    }
})
def get_orders():
    """
    Retrieves paginated orders with optional sorting and metadata.
    """
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        sort_by = request.args.get('sort_by', default='created_at', type=str)
        sort_order = request.args.get('sort_order', default='asc', type=str)
        include_meta = request.args.get('include_meta', default='true').lower() == 'true'

        if page < 1 or per_page < 1 or per_page > 100:
            return error_response("Invalid pagination parameters.")
        if sort_by not in SORTABLE_FIELDS:
            return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}")

        data = OrderService.get_paginated_orders(
            page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
        )

        response = {"orders": orders_schema.dump(data["items"])}
        if include_meta:
            response.update({k: v for k, v in data.items() if k != "items"})

        return jsonify(response), 200
    except Exception as e:
        return error_response(str(e), 500)


# ---------------------------
# Get Order by ID
# ---------------------------
@order_bp.route('/<int:order_id>', methods=['GET'])
@limiter.limit("10 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Orders"],
    "summary": "Retrieve an order by ID",
    "description": "Fetches an order by its unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "order_id", "in": "path", "type": "integer", "required": True, "description": "Order ID."}
    ],
    "responses": {
        "200": {"description": "Order retrieved successfully."},
        "404": {"description": "Order not found."}
    }
})
def get_order(order_id):
    """
    Fetches an order by ID.
    """
    try:
        order = OrderService.get_order_by_id(order_id)
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        return error_response(str(e), 404)


# ---------------------------
# Update Order
# ---------------------------
@order_bp.route('/<int:order_id>', methods=['PUT'])
@limiter.limit("5 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Orders"],
    "summary": "Update an order",
    "description": "Updates an order's quantity by its unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "order_id", "in": "path", "type": "integer", "required": True, "description": "Order ID."},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "quantity": {"type": "integer", "description": "Updated quantity of the order."}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Order updated successfully."},
        "400": {"description": "Validation error."},
        "404": {"description": "Order not found."}
    }
})
def update_order(order_id):
    """
    Updates an order by ID.
    """
    try:
        data = request.get_json()
        validated_data = order_schema.load(data, partial=True)
        order = OrderService.update_order(order_id, quantity=validated_data.get('quantity'))
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Order
# ---------------------------
@order_bp.route('/<int:order_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Orders"],
    "summary": "Delete an order",
    "description": "Deletes an order by its unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "order_id", "in": "path", "type": "integer", "required": True, "description": "Order ID."}
    ],
    "responses": {
        "200": {"description": "Order deleted successfully."},
        "404": {"description": "Order not found."}
    }
})
def delete_order(order_id):
    """
    Deletes an order by ID.
    """
    try:
        OrderService.delete_order(order_id)
        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

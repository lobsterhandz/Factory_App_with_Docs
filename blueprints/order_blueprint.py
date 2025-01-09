from flask import Blueprint, request, jsonify
from services.order_service import OrderService
from schemas.order_schema import order_schema, orders_schema
from utils.utils import error_response, role_required
from limiter import limiter

# Create Blueprint
order_bp = Blueprint('orders', __name__)

# Allowed sortable fields
SORTABLE_FIELDS = ['created_at', 'quantity', 'total_price']


# ---------------------------
# Create an Order
# ---------------------------
@order_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")
@role_required('user')  # Allow 'user' role to create orders
def create_order():
    """
    Creates a new order.

    Request Body:
    - customer_id (int): ID of the customer.
    - product_id (int): ID of the product.
    - quantity (int): Quantity of the product ordered.

    Returns:
    - 201: Created order data.
    - 400: Validation or creation error.
    """
    try:
        data = request.get_json()
        validated_data = order_schema.load(data)

        # Create order
        order = OrderService.create_order(
            customer_id=validated_data['customer_id'],
            product_id=validated_data['product_id'],
            quantity=validated_data['quantity']
        )
        return jsonify(order_schema.dump(order)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Orders
# ---------------------------
@order_bp.route('', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Admin-only access
def get_orders():
    """
    Retrieves paginated orders with optional sorting and metadata.

    Query Parameters:
    - page (int): Page number (default: 1).
    - per_page (int): Records per page (default: 10, max: 100).
    - sort_by (str): Field to sort by ('created_at', 'quantity', 'total_price') (default: 'created_at').
    - sort_order (str): Sorting order ('asc' or 'desc') (default: 'asc').
    - include_meta (bool): Include metadata (default: true).

    Returns:
    - 200: Paginated orders with metadata.
    - 500: Server error.
    """
    try:
        # Pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Sorting parameters
        sort_by = request.args.get('sort_by', default='created_at', type=str)
        sort_order = request.args.get('sort_order', default='asc', type=str)

        # Metadata toggle
        include_meta = request.args.get('include_meta', default='true', type=str).lower() == 'true'

        # Validate inputs
        if page < 1 or per_page < 1 or per_page > 100:
            return error_response("Invalid pagination parameters.")

        if sort_by not in SORTABLE_FIELDS:
            return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}")

        # Fetch paginated orders
        data = OrderService.get_paginated_orders(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            include_meta=include_meta
        )

        # Prepare JSON response
        response = {"orders": orders_schema.dump(data["items"])}
        if include_meta:
            response.update({
                "total": data["total"],
                "pages": data["pages"],
                "page": data["page"],
                "per_page": data["per_page"]
            })

        return jsonify(response), 200
    except Exception as e:
        return error_response(str(e), 500)


# ---------------------------
# Get Order by ID
# ---------------------------
@order_bp.route('/<int:order_id>', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Admin-only access
def get_order(order_id):
    """
    Fetches an order by ID.

    Path Parameters:
    - order_id (int): Order ID.

    Returns:
    - 200: Order data.
    - 404: Order not found.
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
@role_required('admin')  # Admin-only access
def update_order(order_id):
    """
    Updates an order by ID.

    Request Body:
    - quantity (int): Updated quantity.

    Returns:
    - 200: Updated order data.
    - 400: Validation or update error.
    """
    try:
        data = request.get_json()
        validated_data = order_schema.load(data, partial=True)

        # Validate at least one field for update
        if 'quantity' not in validated_data:
            return error_response("At least one field (quantity) is required for update.")

        # Update order
        order = OrderService.update_order(
            order_id,
            quantity=validated_data.get('quantity')
        )
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Order
# ---------------------------
@order_bp.route('/<int:order_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('admin')  # Admin-only access
def delete_order(order_id):
    """
    Deletes an order by ID.

    Returns:
    - 200: Success message.
    - 404: Order not found.
    """
    try:
        OrderService.delete_order(order_id)
        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

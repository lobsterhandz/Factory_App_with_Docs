from flask import Blueprint, request, jsonify
from services.product_service import ProductService
from schemas.product_schema import product_schema, products_schema
from utils.utils import error_response, role_required
from limiter import limiter

# Create Blueprint
product_bp = Blueprint('products', __name__)

# Allowed sortable fields
SORTABLE_FIELDS = ['name', 'price']

# ---------------------------
# Create a Product
# ---------------------------
@product_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")
@role_required('admin')  # Only admin can create products
def create_product():
    """Creates a new product."""
    try:
        data = request.get_json()
        validated_data = product_schema.load(data)

        product = ProductService.create_product(
            name=validated_data['name'],
            price=validated_data['price']
        )
        return jsonify(product_schema.dump(product)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Products
# ---------------------------
@product_bp.route('', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Admin-only access to view all products
def get_products():
    """
    Retrieves paginated products with optional sorting and metadata.

    Query Parameters:
    - page (int): Page number (default: 1)
    - per_page (int): Items per page (default: 10, max: 100)
    - sort_by (str): Field to sort by ('name', 'price') (default: 'name')
    - sort_order (str): Sort order ('asc', 'desc') (default: 'asc')
    - include_meta (bool): Include metadata (default: true)
    """
    try:
        # Pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Sorting parameters
        sort_by = request.args.get('sort_by', default='name', type=str)
        sort_order = request.args.get('sort_order', default='asc', type=str)

        # Metadata toggle
        include_meta = request.args.get('include_meta', default='true', type=str).lower() == 'true'

        # Input validation
        if page < 1 or per_page < 1 or per_page > 100:
            return error_response("Invalid pagination parameters.", 400)

        if sort_by not in SORTABLE_FIELDS:
            return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}", 400)

        # Fetch paginated products
        data = ProductService.get_paginated_products(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            include_meta=include_meta
        )

        # Prepare JSON response
        response = {
            "products": products_schema.dump(data["items"])
        }

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
# Get Product by ID
# ---------------------------
@product_bp.route('/<int:product_id>', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Admin-only access to view a product
def get_product(product_id):
    """Fetches a product by its ID."""
    try:
        product = ProductService.get_product_by_id(product_id)
        return jsonify(product_schema.dump(product)), 200
    except Exception as e:
        return error_response(str(e), 404)


# ---------------------------
# Update Product
# ---------------------------
@product_bp.route('/<int:product_id>', methods=['PUT'])
@limiter.limit("5 per minute")
@role_required('admin')  # Admin-only access to update a product
def update_product(product_id):
    """Updates a product by ID."""
    try:
        data = request.get_json()
        validated_data = product_schema.load(data, partial=True)

        product = ProductService.update_product(
            product_id,
            name=validated_data.get('name'),
            price=validated_data.get('price')
        )
        return jsonify(product_schema.dump(product)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Product
# ---------------------------
@product_bp.route('/<int:product_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('admin')  # Admin-only access to delete a product
def delete_product(product_id):
    """Deletes a product by ID."""
    try:
        ProductService.delete_product(product_id)
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

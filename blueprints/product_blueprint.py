from flask import Blueprint, request, jsonify
from services.product_service import ProductService
from schemas.product_schema import product_schema, products_schema
from utils.utils import error_response, role_required, jwt_required
from limiter import limiter
from flask_caching import Cache
from flasgger.utils import swag_from

# Create Blueprint
product_bp = Blueprint('products', __name__)
cache = Cache()  # Caching instance

# Allowed sortable fields
SORTABLE_FIELDS = ['name', 'price']


# ---------------------------
# Create a Product
# ---------------------------
@product_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')  # Only admin can create products
@swag_from({
    "tags": ["Products"],
    "summary": "Create a new product",
    "description": "Creates a new product with the specified details.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name", "price"],
                "properties": {
                    "name": {"type": "string", "description": "Name of the product."},
                    "price": {"type": "number", "format": "float", "description": "Price of the product."}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "Product created successfully."},
        "400": {"description": "Validation or creation error."},
        "500": {"description": "Internal server error."}
    }
})
def create_product():
    """
    Creates a new product.
    """
    try:
        data = request.get_json()
        validated_data = product_schema.load(data)
        product = ProductService.create_product(**validated_data)
        return jsonify(product_schema.dump(product)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Products
# ---------------------------
@product_bp.route('', methods=['GET'])
@cache.cached(query_string=True)  # Cache GET requests with query parameters
@limiter.limit("10 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')  # Admin-only access
@swag_from({
    "tags": ["Products"],
    "summary": "Retrieve paginated products",
    "description": "Retrieves a paginated list of products with optional sorting and metadata.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "description": "Page number (default: 1)."},
        {"name": "per_page", "in": "query", "type": "integer", "description": "Items per page (default: 10, max: 100)."},
        {"name": "sort_by", "in": "query", "type": "string", "description": "Field to sort by (default: 'name')."},
        {"name": "sort_order", "in": "query", "type": "string", "description": "Sort order ('asc' or 'desc')."},
        {"name": "include_meta", "in": "query", "type": "boolean", "description": "Include metadata (default: true)."}
    ],
    "responses": {
        "200": {
            "description": "Successfully retrieved paginated products.",
            "schema": {
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Product"}
                    },
                    "total": {"type": "integer"},
                    "pages": {"type": "integer"},
                    "page": {"type": "integer"},
                    "per_page": {"type": "integer"}
                }
            }
        },
        "400": {"description": "Invalid parameters."},
        "500": {"description": "Internal server error."}
    }
})
def get_products():
    """
    Retrieves paginated products.
    """
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        sort_by = request.args.get('sort_by', default='name', type=str)
        sort_order = request.args.get('sort_order', default='asc', type=str)
        include_meta = request.args.get('include_meta', default='true').lower() == 'true'

        if page < 1 or per_page < 1 or per_page > 100:
            return error_response("Invalid pagination parameters.", 400)
        if sort_by not in SORTABLE_FIELDS:
            return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}", 400)

        data = ProductService.get_paginated_products(
            page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
        )

        response = {"products": products_schema.dump(data["items"])}
        if include_meta:
            response.update({k: v for k, v in data.items() if k != "items"})

        return jsonify(response), 200
    except Exception as e:
        return error_response(str(e), 500)


# ---------------------------
# Get Product by ID
# ---------------------------
@product_bp.route('/<int:product_id>', methods=['GET'])
@limiter.limit("10 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Products"],
    "summary": "Retrieve a product by ID",
    "description": "Fetches a product by its unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "product_id", "in": "path", "type": "integer", "required": True, "description": "Product ID."}
    ],
    "responses": {
        "200": {"description": "Product retrieved successfully."},
        "404": {"description": "Product not found."}
    }
})
def get_product(product_id):
    """
    Fetches a product by ID.
    """
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
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Products"],
    "summary": "Update a product",
    "description": "Updates a product's details by its unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "product_id", "in": "path", "type": "integer", "required": True, "description": "Product ID."},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Updated name of the product."},
                    "price": {"type": "number", "format": "float", "description": "Updated price of the product."}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Product updated successfully."},
        "400": {"description": "Validation error."},
        "404": {"description": "Product not found."}
    }
})
def update_product(product_id):
    """
    Updates a product by ID.
    """
    try:
        data = request.get_json()
        validated_data = product_schema.load(data, partial=True)
        product = ProductService.update_product(product_id, **validated_data)
        return jsonify(product_schema.dump(product)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Product
# ---------------------------
@product_bp.route('/<int:product_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Products"],
    "summary": "Delete a product",
    "description": "Deletes a product by its unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "product_id", "in": "path", "type": "integer", "required": True, "description": "Product ID."}
    ],
    "responses": {
        "200": {"description": "Product deleted successfully."},
        "404": {"description": "Product not found."}
    }
})
def delete_product(product_id):
    """
    Deletes a product by ID.
    """
    try:
        ProductService.delete_product(product_id)
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

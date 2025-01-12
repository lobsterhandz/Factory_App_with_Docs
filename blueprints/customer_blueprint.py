from flask import Blueprint, request, jsonify
from services.customer_service import CustomerService
from schemas.customer_schema import customer_schema, customers_schema
from utils.utils import error_response, role_required
from flask_jwt_extended import jwt_required
from flask_caching import Cache
from limiter import limiter
from flasgger.utils import swag_from

# Create Blueprint
customer_bp = Blueprint('customers', __name__)
cache = Cache()

# Allowed sortable fields
SORTABLE_FIELDS = ['name', 'email', 'phone']

# ---------------------------
# Create a Customer
# ---------------------------
@customer_bp.route('', methods=['POST'])
@jwt_required()  # Requires valid JWT
@role_required('admin')  # Restrict to admin role
@limiter.limit("5 per minute")  # Rate limiting
@swag_from({
    "tags": ["Customers"],
    "summary": "Create a new customer",
    "description": "Creates a new customer in the system.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name", "email", "phone"],
                "properties": {
                    "name": {"type": "string", "description": "Customer's name."},
                    "email": {"type": "string", "description": "Customer's email."},
                    "phone": {"type": "string", "description": "Customer's phone number."}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "Customer created successfully."},
        "400": {"description": "Validation or creation error."},
        "500": {"description": "Internal server error."}
    }
})
def create_customer():
    """Creates a new customer."""
    try:
        data = request.get_json()
        validated_data = customer_schema.load(data)
        customer = CustomerService.create_customer(**validated_data)
        return jsonify(customer_schema.dump(customer)), 201
    except Exception as e:
        return error_response(str(e))

# ---------------------------
# Get Paginated Customers
# ---------------------------
@customer_bp.route('', methods=['GET'])
@cache.cached(query_string=True)  # Cache GET requests with query parameters
@jwt_required()
@role_required('admin')
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Customers"],
    "summary": "Retrieve paginated customers",
    "description": "Retrieves a paginated list of customers with optional sorting and metadata.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "description": "Page number (default: 1)."},
        {"name": "per_page", "in": "query", "type": "integer", "description": "Items per page (default: 10)."},
        {"name": "sort_by", "in": "query", "type": "string", "description": "Field to sort by (default: 'name')."},
        {"name": "sort_order", "in": "query", "type": "string", "description": "Sort order ('asc' or 'desc')."},
        {"name": "include_meta", "in": "query", "type": "boolean", "description": "Include metadata (default: true)."}
    ],
    "responses": {
        "200": {
            "description": "Successfully retrieved customers.",
            "schema": {
                "type": "object",
                "properties": {
                    "customers": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Customer"}
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
def get_customers():
    """Retrieves paginated customers."""
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

        data = CustomerService.get_paginated_customers(
            page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
        )

        response = {"customers": customers_schema.dump(data["items"])}
        if include_meta:
            response.update({k: v for k, v in data.items() if k != "items"})

        return jsonify(response), 200
    except Exception as e:
        return error_response(str(e), 500)

# ---------------------------
# Get Customer by ID
# ---------------------------
@customer_bp.route('/<int:customer_id>', methods=['GET'])
@cache.cached()  # Cache GET request
@jwt_required()
@role_required('admin')
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Customers"],
    "summary": "Retrieve a customer by ID",
    "description": "Fetches a customer's details by their ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "customer_id", "in": "path", "type": "integer", "required": True, "description": "Customer ID."}
    ],
    "responses": {
        "200": {"description": "Customer retrieved successfully."},
        "404": {"description": "Customer not found."}
    }
})
def get_customer(customer_id):
    """Fetches a customer by ID."""
    try:
        customer = CustomerService.get_customer_by_id(customer_id)
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return error_response(str(e), 404)

# ---------------------------
# Update Customer
# ---------------------------
@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
@limiter.limit("5 per minute")
@swag_from({
    "tags": ["Customers"],
    "summary": "Update a customer",
    "description": "Updates a customer's details by their ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "customer_id", "in": "path", "type": "integer", "required": True, "description": "Customer ID."},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {"$ref": "#/definitions/Customer"}
        }
    ],
    "responses": {
        "200": {"description": "Customer updated successfully."},
        "400": {"description": "Validation error."},
        "404": {"description": "Customer not found."}
    }
})
def update_customer(customer_id):
    """Updates a customer by ID."""
    try:
        data = request.get_json()
        validated_data = customer_schema.load(data, partial=True)
        customer = CustomerService.update_customer(customer_id, **validated_data)
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return error_response(str(e))

# ---------------------------
# Delete Customer
# ---------------------------
@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
@limiter.limit("5 per minute")
@swag_from({
    "tags": ["Customers"],
    "summary": "Delete a customer",
    "description": "Deletes a customer by their unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "customer_id", "in": "path", "type": "integer", "required": True, "description": "Customer ID."}
    ],
    "responses": {
        "200": {"description": "Customer deleted successfully."},
        "404": {"description": "Customer not found."}
    }
})
def delete_customer(customer_id):
    """Deletes a customer by ID."""
    try:
        CustomerService.delete_customer(customer_id)
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

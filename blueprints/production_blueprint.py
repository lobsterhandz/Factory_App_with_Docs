from flask import Blueprint, request, jsonify
from services.production_service import ProductionService
from schemas.production_schema import production_schema, productions_schema
from limiter import limiter
from flask_caching import Cache
from utils.utils import error_response, role_required, jwt_required
from flasgger.utils import swag_from

# Create Blueprint
production_bp = Blueprint('production', __name__)
cache = Cache()  # Caching instance


# ---------------------------
# Create a Production Record
# ---------------------------
@production_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')  # Only admin can create production records
@swag_from({
    "tags": ["Production"],
    "summary": "Create a new production record",
    "description": "Creates a new production record with the specified details.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["product_id", "quantity_produced", "date_produced"],
                "properties": {
                    "product_id": {"type": "integer", "description": "ID of the product produced."},
                    "quantity_produced": {"type": "integer", "description": "Quantity of the product produced."},
                    "date_produced": {"type": "string", "format": "date", "description": "Date of production (YYYY-MM-DD)."}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "Production record created successfully."},
        "400": {"description": "Validation or creation error."},
        "500": {"description": "Internal server error."}
    }
})
def create_production():
    """
    Creates a new production record.
    """
    try:
        data = request.get_json()
        validated_data = production_schema.load(data)
        production = ProductionService.create_production(**validated_data)
        return jsonify(production_schema.dump(production)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Production Records
# ---------------------------
@production_bp.route('', methods=['GET'])
@cache.cached(query_string=True)  # Cache GET requests with query parameters
@limiter.limit("10 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')  # Only admin can view production records
@swag_from({
    "tags": ["Production"],
    "summary": "Retrieve paginated production records",
    "description": "Fetches paginated production records with optional sorting and metadata.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "description": "Page number (default: 1)."},
        {"name": "per_page", "in": "query", "type": "integer", "description": "Items per page (default: 10, max: 100)."},
        {"name": "sort_by", "in": "query", "type": "string", "description": "Sort field (default: 'date_produced')."},
        {"name": "sort_order", "in": "query", "type": "string", "description": "Sort order ('asc' or 'desc')."},
        {"name": "include_meta", "in": "query", "type": "boolean", "description": "Include metadata (default: true)."}
    ],
    "responses": {
        "200": {
            "description": "Paginated production records retrieved successfully.",
            "schema": {
                "type": "object",
                "properties": {
                    "productions": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Production"}
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
def get_productions():
    """
    Retrieves paginated production records.
    """
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        sort_by = request.args.get('sort_by', default='date_produced', type=str)
        sort_order = request.args.get('sort_order', default='asc', type=str)
        include_meta = request.args.get('include_meta', default='true').lower() == 'true'

        data = ProductionService.get_paginated_productions(
            page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
        )

        response = {"productions": productions_schema.dump(data["items"])}
        if include_meta:
            response.update({k: v for k, v in data.items() if k != "items"})

        return jsonify(response), 200
    except Exception as e:
        return error_response(str(e), 500)


# ---------------------------
# Get Production Record by ID
# ---------------------------
@production_bp.route('/<int:production_id>', methods=['GET'])
@limiter.limit("10 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Production"],
    "summary": "Retrieve a production record by ID",
    "description": "Fetches a specific production record by its ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "production_id", "in": "path", "type": "integer", "required": True, "description": "Production ID."}
    ],
    "responses": {
        "200": {"description": "Production record retrieved successfully."},
        "404": {"description": "Production record not found."}
    }
})
def get_production(production_id):
    """
    Fetches a production record by ID.
    """
    try:
        production = ProductionService.get_production_by_id(production_id)
        return jsonify(production_schema.dump(production)), 200
    except Exception as e:
        return error_response(str(e), 404)


# ---------------------------
# Update Production Record
# ---------------------------
@production_bp.route('/<int:production_id>', methods=['PUT'])
@limiter.limit("5 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Production"],
    "summary": "Update a production record",
    "description": "Updates a production record's details by its ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "production_id", "in": "path", "type": "integer", "required": True, "description": "Production ID."},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "quantity_produced": {"type": "integer", "description": "Updated quantity of the product produced."},
                    "date_produced": {"type": "string", "format": "date", "description": "Updated production date."}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Production record updated successfully."},
        "400": {"description": "Validation error."},
        "404": {"description": "Production record not found."}
    }
})
def update_production(production_id):
    """
    Updates a production record by ID.
    """
    try:
        data = request.get_json()
        validated_data = production_schema.load(data, partial=True)
        production = ProductionService.update_production(production_id, **validated_data)
        return jsonify(production_schema.dump(production)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Production Record
# ---------------------------
@production_bp.route('/<int:production_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@jwt_required  # Requires valid JWT token
@role_required('admin')
@swag_from({
    "tags": ["Production"],
    "summary": "Delete a production record",
    "description": "Deletes a production record by its ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "production_id", "in": "path", "type": "integer", "required": True, "description": "Production ID."}
    ],
    "responses": {
        "200": {"description": "Production record deleted successfully."},
        "404": {"description": "Production record not found."}
    }
})
def delete_production(production_id):
    """
    Deletes a production record by ID.
    """
    try:
        ProductionService.delete_production(production_id)
        return jsonify({"message": "Production record deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

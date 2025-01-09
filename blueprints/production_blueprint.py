from flask import Blueprint, request, jsonify
from services.production_service import ProductionService
from schemas.production_schema import production_schema, productions_schema
from limiter import limiter
from utils.utils import error_response, role_required  # Import role-based access and error handling

# Create Blueprint
production_bp = Blueprint('production', __name__)

# ---------------------------
# Create a Production Record
# ---------------------------
@production_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")
@role_required('admin')  # Only admin can create production records
def create_production():
    """Creates a new production record."""
    try:
        data = request.get_json()
        validated_data = production_schema.load(data)

        # Create production record
        production = ProductionService.create_production(
            product_id=validated_data['product_id'],
            quantity_produced=validated_data['quantity_produced'],
            date_produced=validated_data['date_produced']
        )
        return jsonify(production_schema.dump(production)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Production Records
# ---------------------------
@production_bp.route('', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Only admin can view production records
def get_productions():
    """
    Retrieves paginated production records.

    Query Parameters:
    - page (int): Page number (default: 1).
    - per_page (int): Items per page (default: 10, max: 100).
    - sort_by (str): Field to sort by ('date_produced', 'quantity_produced') (default: 'date_produced').
    - sort_order (str): Sort order ('asc', 'desc') (default: 'asc').
    - include_meta (bool): Include metadata (default: true).

    Example:
    GET /production?page=2&per_page=5&sort_by=quantity_produced&sort_order=desc
    """
    try:
        # Query parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        sort_by = request.args.get('sort_by', default='date_produced', type=str)
        sort_order = request.args.get('sort_order', default='asc', type=str)
        include_meta = request.args.get('include_meta', default='true', type=str).lower() == 'true'

        # Fetch paginated records
        data = ProductionService.get_paginated_productions(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            include_meta=include_meta
        )

        # Build response
        response = {"productions": productions_schema.dump(data["items"])}
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
# Get Production Record by ID
# ---------------------------
@production_bp.route('/<int:production_id>', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Only admin can view a specific production record
def get_production(production_id):
    """Fetches a production record by ID."""
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
@role_required('admin')  # Only admin can update production records
def update_production(production_id):
    """Updates a production record by ID."""
    try:
        data = request.get_json()
        validated_data = production_schema.load(data, partial=True)

        production = ProductionService.update_production(
            production_id,
            quantity_produced=validated_data.get('quantity_produced'),
            date_produced=validated_data.get('date_produced')
        )
        return jsonify(production_schema.dump(production)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Production Record
# ---------------------------
@production_bp.route('/<int:production_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('admin')  # Only admin can delete production records
def delete_production(production_id):
    """Deletes a production record by ID."""
    try:
        ProductionService.delete_production(production_id)
        return jsonify({"message": "Production record deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

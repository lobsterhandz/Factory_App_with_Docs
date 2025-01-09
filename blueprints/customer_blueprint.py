from flask import Blueprint, request, jsonify
from services.customer_service import CustomerService
from schemas.customer_schema import customer_schema, customers_schema
from utils.utils import error_response, role_required
from limiter import limiter

# Create Blueprint
customer_bp = Blueprint('customers', __name__)

# Allowed sortable fields
SORTABLE_FIELDS = ['name', 'email', 'phone']

# ---------------------------
# Create a Customer
# ---------------------------
@customer_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting
@role_required('admin')  # Restrict to admin role
def create_customer():
    """Creates a new customer."""
    try:
        # Parse and validate input data
        data = request.get_json()
        validated_data = customer_schema.load(data)

        # Create a customer
        customer = CustomerService.create_customer(
            name=validated_data['name'],
            email=validated_data['email'],
            phone=validated_data['phone']
        )
        return jsonify(customer_schema.dump(customer)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Customers
# ---------------------------
@customer_bp.route('', methods=['GET'])
@limiter.limit("10 per minute")  # Rate limiting
@role_required('admin')  # Restrict to admin role
def get_customers():
    """
    Retrieves paginated customers with optional sorting and metadata.

    Query Parameters:
    - page (int): Page number (default: 1)
    - per_page (int): Items per page (default: 10, max: 100)
    - sort_by (str): Field to sort by ('name', 'email', 'phone') (default: 'name')
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

        # Validate bounds
        if page < 1 or per_page < 1 or per_page > 100:
            return error_response("Invalid pagination parameters.", 400)

        # Validate sorting fields
        if sort_by not in SORTABLE_FIELDS:
            return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}", 400)

        # Fetch paginated customers
        data = CustomerService.get_paginated_customers(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            include_meta=include_meta
        )

        # Prepare JSON response
        response = {
            "customers": customers_schema.dump(data["items"])
        }

        # Add metadata if enabled
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
# Get Customer by ID
# ---------------------------
@customer_bp.route('/<int:customer_id>', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Restrict to admin role
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
@limiter.limit("5 per minute")
@role_required('admin')  # Restrict to admin role
def update_customer(customer_id):
    """Updates a customer by ID."""
    try:
        # Parse and validate input data
        data = request.get_json()
        validated_data = customer_schema.load(data, partial=True)

        # Update customer
        customer = CustomerService.update_customer(
            customer_id,
            name=validated_data.get('name'),
            email=validated_data.get('email'),
            phone=validated_data.get('phone')
        )
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Customer
# ---------------------------
@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('admin')  # Restrict to admin role
def delete_customer(customer_id):
    """Deletes a customer by ID."""
    try:
        CustomerService.delete_customer(customer_id)
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

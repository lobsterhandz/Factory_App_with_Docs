from flask import Blueprint, request, jsonify
from services.employee_service import EmployeeService
from schemas.employee_schema import employee_schema, employees_schema
from utils.utils import error_response, role_required
from limiter import limiter
from flasgger.utils import swag_from

# Create Blueprint
employee_bp = Blueprint('employees', __name__)

# Allowed sortable fields
SORTABLE_FIELDS = ['name', 'position', 'email', 'phone']

# ---------------------------
# Create an Employee
# ---------------------------
@employee_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting to prevent abuse
@role_required('admin')  # Restrict to admin role
@swag_from({
    "tags": ["Employees"],
    "summary": "Create a new employee",
    "description": "Creates a new employee in the system.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name", "position", "email", "phone"],
                "properties": {
                    "name": {"type": "string", "description": "Employee's name."},
                    "position": {"type": "string", "description": "Job position."},
                    "email": {"type": "string", "description": "Employee's email."},
                    "phone": {"type": "string", "description": "Employee's phone number."}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "Employee created successfully."},
        "400": {"description": "Validation or creation error."},
        "500": {"description": "Internal server error."}
    }
})
def create_employee():
    """
    Creates a new employee.
    """
    try:
        data = request.get_json()
        validated_data = employee_schema.load(data)
        employee = EmployeeService.create_employee(**validated_data)
        return jsonify(employee_schema.dump(employee)), 201
    except Exception as e:
        return error_response(str(e))

# ---------------------------
# Get Paginated Employees
# ---------------------------
@employee_bp.route('', methods=['GET'])
@limiter.limit("10 per minute")  # Rate limiting for protection
@role_required('admin')  # Restrict to admin role
@swag_from({
    "tags": ["Employees"],
    "summary": "Retrieve paginated employees",
    "description": "Retrieves paginated employees with optional sorting and metadata.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "description": "Page number (default: 1)."},
        {"name": "per_page", "in": "query", "type": "integer", "description": "Records per page (default: 10)."},
        {"name": "sort_by", "in": "query", "type": "string", "description": "Sorting field (default: 'name')."},
        {"name": "sort_order", "in": "query", "type": "string", "description": "Sorting order ('asc' or 'desc')."}
    ],
    "responses": {
        "200": {
            "description": "Paginated employee data.",
            "schema": {
                "type": "object",
                "properties": {
                    "employees": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Employee"}
                    },
                    "total": {"type": "integer"},
                    "pages": {"type": "integer"},
                    "page": {"type": "integer"},
                    "per_page": {"type": "integer"}
                }
            }
        },
        "500": {"description": "Server error during query."}
    }
})
def get_employees():
    """
    Retrieves paginated employees with optional sorting and metadata.
    """
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        sort_by = request.args.get('sort_by', default='name', type=str)
        sort_order = request.args.get('sort_order', default='asc', type=str)
        include_meta = request.args.get('include_meta', default='true').lower() == 'true'

        if page < 1 or per_page < 1 or per_page > 100:
            return error_response("Invalid pagination parameters.")
        if sort_by not in SORTABLE_FIELDS:
            return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}")

        data = EmployeeService.get_paginated_employees(
            page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=include_meta
        )

        response = {"employees": employees_schema.dump(data["items"])}
        if include_meta:
            response.update({k: v for k, v in data.items() if k != "items"})

        return jsonify(response), 200
    except Exception as e:
        return error_response(str(e), 500)

# ---------------------------
# Get Employee by ID
# ---------------------------
@employee_bp.route('/<int:employee_id>', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')
@swag_from({
    "tags": ["Employees"],
    "summary": "Retrieve employee by ID",
    "description": "Fetches an employee by their unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "employee_id", "in": "path", "type": "integer", "required": True, "description": "Employee ID."}
    ],
    "responses": {
        "200": {"description": "Employee retrieved successfully."},
        "404": {"description": "Employee not found."}
    }
})
def get_employee(employee_id):
    """
    Fetches an employee by ID.
    """
    try:
        employee = EmployeeService.get_employee_by_id(employee_id)
        return jsonify(employee_schema.dump(employee)), 200
    except Exception as e:
        return error_response(str(e), 404)

# ---------------------------
# Update Employee
# ---------------------------
@employee_bp.route('/<int:employee_id>', methods=['PUT'])
@limiter.limit("5 per minute")
@role_required('admin')
@swag_from({
    "tags": ["Employees"],
    "summary": "Update an employee",
    "description": "Updates an employee's details by ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "employee_id", "in": "path", "type": "integer", "required": True, "description": "Employee ID."},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {"$ref": "#/definitions/Employee"}
        }
    ],
    "responses": {
        "200": {"description": "Employee updated successfully."},
        "400": {"description": "Validation error."},
        "404": {"description": "Employee not found."}
    }
})
def update_employee(employee_id):
    """
    Updates an employee by ID.
    """
    try:
        data = request.get_json()
        validated_data = employee_schema.load(data, partial=True)
        employee = EmployeeService.update_employee(employee_id, **validated_data)
        return jsonify(employee_schema.dump(employee)), 200
    except Exception as e:
        return error_response(str(e))

# ---------------------------
# Delete Employee
# ---------------------------
@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('admin')
@swag_from({
    "tags": ["Employees"],
    "summary": "Delete an employee",
    "description": "Deletes an employee by their unique ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "employee_id", "in": "path", "type": "integer", "required": True, "description": "Employee ID."}
    ],
    "responses": {
        "200": {"description": "Employee deleted successfully."},
        "404": {"description": "Employee not found."}
    }
})
def delete_employee(employee_id):
    """
    Deletes an employee by ID.
    """
    try:
        EmployeeService.delete_employee(employee_id)
        return jsonify({"message": "Employee deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

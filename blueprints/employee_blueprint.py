from flask import Blueprint, request, jsonify
from services.employee_service import EmployeeService
from schemas.employee_schema import employee_schema, employees_schema
from utils.utils import error_response, role_required
from limiter import limiter

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
def create_employee():
    """
    Creates a new employee.

    Request Body:
    - name (str): Employee's name.
    - position (str): Job position.
    - email (str): Employee email.
    - phone (str): Employee phone.

    Returns:
    - 201: Created employee data.
    - 400: Validation or creation error.
    """
    try:
        # Parse and validate input data
        data = request.get_json()
        validated_data = employee_schema.load(data)

        # Create an employee
        employee = EmployeeService.create_employee(
            name=validated_data['name'],
            position=validated_data['position'],
            email=validated_data['email'],
            phone=validated_data['phone']
        )
        return jsonify(employee_schema.dump(employee)), 201
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get Paginated Employees
# ---------------------------
@employee_bp.route('', methods=['GET'])
@limiter.limit("10 per minute")  # Rate limiting for protection
@role_required('admin')  # Restrict to admin role
def get_employees():
    """
    Retrieves paginated employees with optional sorting and metadata.

    Query Parameters:
    - page (int): Page number (default: 1)
    - per_page (int): Records per page (default: 10, max: 100)
    - sort_by (str): Sorting field ('name', 'position', 'email', 'phone') (default: 'name')
    - sort_order (str): Sorting order ('asc' or 'desc') (default: 'asc')
    - include_meta (bool): Include metadata (default: true)

    Returns:
    - 200: Paginated employee data.
    - 500: Server error during query.
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

        # Validate pagination
        if page < 1 or per_page < 1 or per_page > 100:
            return error_response("Invalid pagination parameters.")

        # Validate sorting fields
        if sort_by not in SORTABLE_FIELDS:
            return error_response(f"Invalid sort_by field. Allowed: {SORTABLE_FIELDS}")

        # Fetch paginated employees
        data = EmployeeService.get_paginated_employees(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            include_meta=include_meta
        )

        # Prepare JSON response
        response = {"employees": employees_schema.dump(data["items"])}
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
# Get Employee by ID
# ---------------------------
@employee_bp.route('/<int:employee_id>', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')  # Restrict to admin role
def get_employee(employee_id):
    """
    Fetches an employee by ID.

    Path Parameters:
    - employee_id (int): Employee ID.

    Returns:
    - 200: Employee data.
    - 404: Employee not found.
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
@role_required('admin')  # Restrict to admin role
def update_employee(employee_id):
    """
    Updates an employee by ID.

    Request Body (optional):
    - name (str): Updated name.
    - position (str): Updated position.
    - email (str): Updated email.
    - phone (str): Updated phone.

    Returns:
    - 200: Updated employee data.
    - 400: Validation or update error.
    """
    try:
        # Parse and validate input data
        data = request.get_json()
        validated_data = employee_schema.load(data, partial=True)

        # Update employee
        employee = EmployeeService.update_employee(
            employee_id,
            name=validated_data.get('name'),
            position=validated_data.get('position'),
            email=validated_data.get('email'),
            phone=validated_data.get('phone')
        )
        return jsonify(employee_schema.dump(employee)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete Employee
# ---------------------------
@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('admin')  # Restrict to admin role
def delete_employee(employee_id):
    """
    Deletes an employee by ID.

    Path Parameters:
    - employee_id (int): Employee ID.

    Returns:
    - 200: Success message.
    - 404: Employee not found.
    """
    try:
        EmployeeService.delete_employee(employee_id)
        return jsonify({"message": "Employee deleted successfully"}), 200
    except Exception as e:
        return error_response(str(e), 404)

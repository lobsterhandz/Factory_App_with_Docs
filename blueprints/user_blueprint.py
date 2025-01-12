from flask import Blueprint, request, jsonify
from models.user import User
from schemas.user_schema import user_schema, users_schema
from utils.utils import encode_token, role_required, error_response
from limiter import limiter
from sqlalchemy.exc import IntegrityError
from flasgger.utils import swag_from
from flask_caching import Cache

# Create Blueprint and Cache
user_bp = Blueprint('user', __name__)
cache = Cache()

# ---------------------------
# User Registration
# ---------------------------
@user_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
@role_required('super_admin')  # Only super_admin can register new admins
@swag_from({
    "tags": ["Users"],
    "summary": "Register a new user",
    "description": "Registers a new user with username, password, and role.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["username", "password", "role"],
                "properties": {
                    "username": {"type": "string", "description": "Unique username for the user."},
                    "password": {"type": "string", "description": "Password for the user."},
                    "role": {"type": "string", "enum": ["super_admin", "admin", "user"], "description": "Role of the user."}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "User registered successfully."},
        "400": {"description": "Validation error or username already exists."},
        "500": {"description": "Internal server error."}
    }
})
def register_user():
    """Registers a new user (admin or user)."""
    try:
        from services.user_service import UserService  # Delayed import
        data = user_schema.load(request.get_json())
        new_user = UserService.create_user(**data)
        return jsonify(user_schema.dump(new_user)), 201
    except IntegrityError:
        return error_response("Username already exists.", 400)
    except Exception as e:
        return error_response(str(e), 500)


# ---------------------------
# User Login
# ---------------------------
@user_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Users"],
    "summary": "User login",
    "description": "Authenticates a user and returns a JWT token.",
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["username", "password"],
                "properties": {
                    "username": {"type": "string", "description": "User's username."},
                    "password": {"type": "string", "description": "User's password."}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Login successful with a JWT token."},
        "400": {"description": "Validation error."},
        "401": {"description": "Invalid credentials."},
        "500": {"description": "Internal server error."}
    }
})
def login_user():
    """Authenticates a user and generates a JWT token."""
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return error_response("Both username and password are required.", 400)

        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            token = encode_token(user.id, user.role)
            return jsonify({"token": token}), 200
        return error_response("Invalid credentials.", 401)
    except Exception as e:
        return error_response(str(e), 500)


# ---------------------------
# Get User Details
# ---------------------------
@user_bp.route('/<int:user_id>', methods=['GET'])
@cache.cached(query_string=True)  # Cache the GET request with query parameters
@limiter.limit("10 per minute")
@role_required('super_admin')  # Requires JWT for super_admin
@swag_from({
    "tags": ["Users"],
    "summary": "Fetch user details",
    "description": "Fetches user details by their ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "user_id", "in": "path", "type": "integer", "required": True, "description": "ID of the user to retrieve."}
    ],
    "responses": {
        "200": {"description": "User details retrieved successfully."},
        "404": {"description": "User not found."},
        "500": {"description": "Internal server error."}
    }
})
def get_user(user_id):
    """Fetches user details by ID."""
    try:
        from services.user_service import UserService
        user = UserService.get_user_by_id(user_id)
        return jsonify(user_schema.dump(user)), 200
    except Exception as e:
        return error_response(str(e), 404)
# ---------------------------
# Update User
# ---------------------------
@user_bp.route('/<int:user_id>', methods=['PUT'])
@limiter.limit("5 per minute")
@role_required('super_admin')
@swag_from({
    "tags": ["Users"],
    "summary": "Update user details",
    "description": "Updates user details such as password and role.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "user_id", "in": "path", "type": "integer", "required": True, "description": "ID of the user to update."},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "New password for the user."},
                    "role": {"type": "string", "enum": ["super_admin", "admin", "user"], "description": "Updated role of the user."}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "User updated successfully."},
        "400": {"description": "Validation or update error."},
        "404": {"description": "User not found."}
    }
})
def update_user(user_id):
    """Updates user details (only by super_admin)."""
    try:
        from services.user_service import UserService
        data = request.get_json()
        updated_user = UserService.update_user(user_id, **data)
        return jsonify(user_schema.dump(updated_user)), 200
    except Exception as e:
        return error_response(str(e), 500)


# ---------------------------
# Delete User
# ---------------------------
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('super_admin')
@swag_from({
    "tags": ["Users"],
    "summary": "Delete user",
    "description": "Deletes a user by their ID.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "user_id", "in": "path", "type": "integer", "required": True, "description": "ID of the user to delete."}
    ],
    "responses": {
        "200": {"description": "User deleted successfully."},
        "404": {"description": "User not found."},
        "500": {"description": "Internal server error."}
    }
})
def delete_user(user_id):
    """Deletes a user by ID."""
    try:
        from services.user_service import UserService
        UserService.delete_user(user_id)
        return jsonify({"message": "User deleted successfully."}), 200
    except Exception as e:
        return error_response(str(e), 404)


# ---------------------------
# List All Users
# ---------------------------
@user_bp.route('', methods=['GET'])
@cache.cached(query_string=True)  # Cache the GET request with query parameters
@limiter.limit("10 per minute")
@role_required('admin')  # Admin role required to list users
@swag_from({
    "tags": ["Users"],
    "summary": "List all users",
    "description": "Lists all users with pagination and sorting.",
    "security": [{"Bearer": []}],
    "parameters": [
        {"name": "page", "in": "query", "type": "integer", "description": "Page number (default: 1)."},
        {"name": "per_page", "in": "query", "type": "integer", "description": "Items per page (default: 10)."},
        {"name": "sort_by", "in": "query", "type": "string", "description": "Field to sort by (default: 'username')."},
        {"name": "sort_order", "in": "query", "type": "string", "description": "Sort order ('asc' or 'desc')."}
    ],
    "responses": {
        "200": {"description": "List of users retrieved successfully."},
        "500": {"description": "Internal server error."}
    }
})
def list_users():
    """Lists all users with pagination and sorting."""
    try:
        from services.user_service import UserService
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'username', type=str)
        sort_order = request.args.get('sort_order', 'asc', type=str)

        data = UserService.get_paginated_users(
            page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, include_meta=True
        )

        response = {
            "users": users_schema.dump(data["items"]),
            "total": data["total"],
            "pages": data["pages"],
            "page": data["page"],
            "per_page": data["per_page"]
        }
        return jsonify(response), 200
    except Exception as e:
        return error_response(str(e), 500)

from flask import Blueprint, request, jsonify
from models.user import User
from schemas.user_schema import user_schema, users_schema
from utils.utils import encode_token, decode_token, role_required, error_response
from limiter import limiter
from sqlalchemy.exc import IntegrityError

# Create Blueprint
user_bp = Blueprint('user', __name__)

# ---------------------------
# User Registration
# ---------------------------
@user_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
@role_required('super_admin')  # Only super_admin can register new admins
def register_user():
    """Registers a new user (admin or user)."""
    try:
        from services.user_service import UserService  # Delayed import
        # Validate inputs using schema
        data = user_schema.load(request.get_json())

        # Create user via service
        new_user = UserService.create_user(
            username=data['username'],
            password=data['password'],
            role=data['role']
        )
        return jsonify(user_schema.dump(new_user)), 201
    except IntegrityError:
        db.session.rollback()
        return error_response("Username already exists.")
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# User Login
# ---------------------------
@user_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login_user():
    """Authenticates a user and generates a JWT token."""
    try:
        # Validate inputs using schema
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return error_response("Both username and password are required.", 400)

        # Authenticate user
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            token = encode_token(user.id, user.role)
            return jsonify({"token": token}), 200
        return error_response("Invalid credentials.", 401)
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Get User Details
# ---------------------------
@user_bp.route('/<int:user_id>', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('super_admin')
def get_user(user_id):
    """Fetches user details by ID."""
    try:
        from services.user_service import UserService  # Delayed import
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
def update_user(user_id):
    """Updates user details (only by super_admin)."""
    try:
        from services.user_service import UserService  # Delayed import
        data = request.get_json()

        # Update user via service
        updated_user = UserService.update_user(
            user_id,
            password=data.get('password'),
            role=data.get('role')
        )
        return jsonify(user_schema.dump(updated_user)), 200
    except Exception as e:
        return error_response(str(e))


# ---------------------------
# Delete User
# ---------------------------
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@role_required('super_admin')
def delete_user(user_id):
    """Deletes a user by ID (only by super_admin)."""
    try:
        from services.user_service import UserService  # Delayed import
        UserService.delete_user(user_id)
        return jsonify({"message": "User deleted successfully."}), 200
    except Exception as e:
        return error_response(str(e), 404)


# ---------------------------
# List All Users (Admin Only)
# ---------------------------
@user_bp.route('', methods=['GET'])
@limiter.limit("10 per minute")
@role_required('admin')
def list_users():
    """Lists all users (admin-level access)."""
    try:
        from services.user_service import UserService  # Delayed import
        # Pagination query params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'username', type=str)
        sort_order = request.args.get('sort_order', 'asc', type=str)

        # Fetch paginated users via service
        data = UserService.get_paginated_users(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            include_meta=True
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
        return error_response(str(e))

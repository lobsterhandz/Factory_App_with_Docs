import jwt
import datetime
from flask import request, jsonify
from functools import wraps
from config import Config


# ---------------------------
# Error Response Utility
# ---------------------------
def error_response(message, status_code=400):
    """Generates a standardized error response."""
    return jsonify({"error": message}), status_code


# ---------------------------
# JWT Token Handling
# ---------------------------
def encode_token(user_id, role):
    """
    Generates a JWT token with user ID and role as payload.
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),  # Expires in 1 day
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
            'role': role
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    except Exception as e:
        return str(e)


import jwt
from config import Config

def decode_token(token):
    """
    Decodes a JWT token and returns its payload.
    """
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:  # Adjusted for newer pyjwt versions
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


# ---------------------------
# Role-Based Access Control
# ---------------------------
def role_required(required_role):
    """
    Decorator to enforce role-based access control.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract Authorization header
            token = request.headers.get('Authorization')

            if not token:
                return error_response("Token is missing!", 403)

            try:
                # Extract Bearer token
                token = token.split(" ")[1]
                payload = decode_token(token)

                # Handle token errors
                if isinstance(payload, str):  # Token decoding issues
                    return error_response(payload, 403)

                # Check if the user role meets the requirement
                user_role = payload['role']
                if user_role != required_role and user_role != 'super_admin':
                    return error_response("Unauthorized access!", 403)

            except Exception as e:
                return error_response("Token is invalid!", 403)

            return f(*args, **kwargs)

        return decorated_function
    return decorator


# ---------------------------
# Token Verification Endpoint
# ---------------------------
def verify_token(token):
    """
    Verifies if a token is valid and returns its payload or an error.
    """
    payload = decode_token(token)
    if isinstance(payload, str):  # Error messages
        return False, payload
    return True, payload

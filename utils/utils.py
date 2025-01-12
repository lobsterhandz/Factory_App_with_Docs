import jwt
import datetime
import logging
from flask import request, jsonify
from functools import wraps
from config import Config

# Initialize Logger
logger = logging.getLogger(__name__)

# ---------------------------
# Error Response Utility
# ---------------------------
def error_response(message, status_code=400):
    logger.warning(f"Error {status_code}: {message}")
    response = {"error": message}
    if Config.DEBUG:  # Add stack trace in debug mode
        import traceback
        response["traceback"] = traceback.format_exc()
    return jsonify(response), status_code

# ---------------------------
# JWT Token Handling
# ---------------------------
def encode_token(user_id, role):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=Config.TOKEN_EXPIRY_DAYS),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
            'role': role
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        logger.info(f"Token generated for user {user_id} with role {role}.")
        return token
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        return str(e)

def decode_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired.")
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        logger.warning("Invalid token.")
        return 'Invalid token. Please log in again.'

# ---------------------------
# JWT Required Decorator
# ---------------------------
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return error_response("Token is missing!", 403)
        try:
            token = token.split(" ")[1]
            payload = decode_token(token)
            if isinstance(payload, str):
                return error_response(payload, 403)
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return error_response("Token is invalid!", 403)
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Role-Based Access Control
# ---------------------------
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return error_response("Token is missing!", 403)
            try:
                token = token.split(" ")[1]
                payload = decode_token(token)
                if isinstance(payload, str):
                    return error_response(payload, 403)
                user_role = payload['role']
                if user_role != required_role and user_role != 'super_admin':
                    logger.warning(f"Unauthorized role: {user_role}")
                    return error_response("Unauthorized access!", 403)
            except Exception as e:
                logger.error(f"Token validation error: {e}")
                return error_response("Token is invalid!", 403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ---------------------------
# Pagination Helper
# ---------------------------
def paginate(query, page, per_page, schema=None):
    items = query.paginate(page, per_page, False)
    return {
        "items": schema.dump(items.items) if schema else [item.to_dict() for item in items.items],
        "total": items.total,
        "pages": items.pages,
        "page": items.page,
        "per_page": items.per_page
    }

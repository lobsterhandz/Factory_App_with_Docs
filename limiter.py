from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the Limiter globally
limiter = Limiter(
    key_func=get_remote_address,  # Use the remote address for rate limiting
    default_limits=["200 per day", "50 per hour"]  # Set default rate limits
)

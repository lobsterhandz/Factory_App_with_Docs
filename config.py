import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration with default settings."""
    
    # General Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')  # Default secret if not set
    DEBUG = False

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/factory_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance
    SQLALCHEMY_ECHO = False  # Set to True for SQL query logs (useful for debugging)

    # Rate Limiter Settings
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200 per day;50 per hour')
    RATELIMIT_HEADERS_ENABLED = True

    # Security Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret_key_here')
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'salt_key_here')

    def __init__(self):
        """Ensure that necessary environment variables are set."""
        self._check_required_env_variables()

    def _check_required_env_variables(self):
        """Check if required environment variables are set and log if missing."""
        required_vars = ['SECRET_KEY', 'DATABASE_URL', 'JWT_SECRET_KEY', 'PASSWORD_SALT']
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Missing required environment variable: {var}")
    

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Enable query logging for development


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    RATELIMIT_DEFAULT = '1000 per day;200 per hour'


# Map environment names to their respective config classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

from flask_sqlalchemy import SQLAlchemy

# Initialize the database object
db = SQLAlchemy()

# Import models AFTER db initialization to avoid circular imports
from .employee import Employee
from .product import Product
from .order import Order
from .customer import Customer
from .production import Production
from .user import User
# Control explicit exports
__all__ = ["db", "Employee", "Product", "Order", "Customer", "Production", "User"]

# Optional logging for debugging purposes
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Database initialized and models imported.")

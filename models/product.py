from models import db
from sqlalchemy.sql import func
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)  # Add stock_quantity column
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    orders = db.relationship('Order', back_populates='product', overlaps="product_orders")
    productions = db.relationship('Production', back_populates='product', overlaps="product_productions")

    # ---------------------------
    # Soft Deletion
    # ---------------------------
    def soft_delete(self):
        """Marks the product as deleted without removing it."""
        self.deleted_at = datetime.utcnow()  # Use client-side timestamp
        db.session.commit()

    # ---------------------------
    # Restore Deleted Product
    # ---------------------------
    def restore(self):
        """Restores a soft-deleted product."""
        self.deleted_at = None
        db.session.commit()

    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        """Converts the model instance into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock_quantity": self.stock_quantity,  # Include stock_quantity in the dict
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<Product {self.name} - ${self.price}>"

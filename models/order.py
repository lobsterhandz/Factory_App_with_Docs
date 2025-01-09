from models import db
from sqlalchemy.sql import func
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    customer = db.relationship('Customer', back_populates='orders', overlaps="customer_orders")
    product = db.relationship('Product', back_populates='orders', overlaps="product_orders")

    # ---------------------------
    # Soft Deletion
    # ---------------------------
    def soft_delete(self):
        """Marks the order as deleted without removing it."""
        self.deleted_at = datetime.utcnow()  # Use client-side timestamp
        db.session.commit()

    # ---------------------------
    # Restore Deleted Order
    # ---------------------------
    def restore(self):
        """Restores a soft-deleted order."""
        self.deleted_at = None
        db.session.commit()

    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        """Converts the model instance into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "customer": {
                "id": self.customer.id,
                "name": self.customer.name,
                "email": self.customer.email
            } if self.customer else None,
            "product": {
                "id": self.product.id,
                "name": self.product.name,
                "price": self.product.price
            } if self.product else None
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<Order {self.id} - ${self.total_price}>"

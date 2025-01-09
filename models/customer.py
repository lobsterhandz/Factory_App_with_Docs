from models import db
from sqlalchemy.sql import func


class Customer(db.Model):
    __tablename__ = 'customers'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    orders = db.relationship('Order', back_populates='customer', lazy='joined')

    # ---------------------------
    # Soft Deletion Methods
    # ---------------------------
    def soft_delete(self):
        """Marks the customer as deleted without removing it."""
        self.deleted_at = func.now()
        db.session.commit()

    def restore(self):
        """Restores a soft-deleted customer."""
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
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<Customer {self.name} - {self.email}>"

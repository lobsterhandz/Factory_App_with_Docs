from models import db
from sqlalchemy.sql import func
from datetime import datetime


class Employee(db.Model):
    __tablename__ = 'employees'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Indexed for fast lookups
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Indexed for fast lookups
    created_at = db.Column(db.DateTime, default=func.current_timestamp())  # Timestamp for creation
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())  # Timestamp for updates
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete marker

    # Relationships (Optional for scalability)
    # orders = db.relationship('Order', backref='employee', lazy='dynamic')

    # ---------------------------
    # Soft Deletion
    # ---------------------------
    def soft_delete(self):
        """Marks the employee as deleted without removing it."""
        self.deleted_at = datetime.utcnow()  # Updated to use client-side timestamps
        db.session.commit()

    # ---------------------------
    # Restore Deleted Employee
    # ---------------------------
    def restore(self):
        """Restores a soft-deleted employee."""
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
            "position": self.position,
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
        return f"<Employee {self.name} - {self.position}>"

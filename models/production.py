from models import db
from sqlalchemy.sql import func
from datetime import datetime


class Production(db.Model):
    __tablename__ = 'production'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_produced = db.Column(db.Integer, nullable=False)
    date_produced = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    product = db.relationship('Product', back_populates='productions', overlaps="product_productions")

    def __repr__(self):
        return f"<Production {self.product_id} - {self.quantity_produced}>"

    # ---------------------------
    # Soft Deletion
    # ---------------------------
    def soft_delete(self):
        """Marks the production record as deleted without removing it."""
        self.deleted_at = datetime.utcnow()  # Use client-side timestamp
        db.session.commit()

    # ---------------------------
    # Restore Deleted Production
    # ---------------------------
    def restore(self):
        """Restores a soft-deleted production record."""
        self.deleted_at = None
        db.session.commit()

    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        """Converts the model instance into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity_produced": self.quantity_produced,
            "date_produced": self.date_produced.strftime("%Y-%m-%d"),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<Production {self.product_id} - {self.quantity_produced}>"

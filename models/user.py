from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

# Role Hierarchy for Access Control
ROLE_HIERARCHY = {
    'super_admin': 3,
    'admin': 2,
    'user': 1
}


class User(db.Model):
    __tablename__ = 'users'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'super_admin', 'admin', or 'user'
    is_active = db.Column(db.Boolean, default=True)  # Soft delete status
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft deletion timestamp

    # ---------------------------
    # Password Management
    # ---------------------------
    def set_password(self, password):
        """Hash and store the password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password, password)

    # ---------------------------
    # Role Management
    # ---------------------------
    def is_super_admin(self):
        """Check if the user is a super admin."""
        return self.role == 'super_admin'

    def is_admin(self):
        """Check if the user is an admin."""
        return self.role == 'admin'

    def has_permission(self, required_role):
        """
        Checks if the user has sufficient permissions based on role hierarchy.
        Example: 'super_admin' can act as 'admin'.
        """
        return ROLE_HIERARCHY[self.role] >= ROLE_HIERARCHY[required_role]

    # ---------------------------
    # Soft Delete Management
    # ---------------------------
    def soft_delete(self):
        """Marks the user as inactive (soft delete)."""
        self.is_active = False
        self.deleted_at = func.now()
        db.session.commit()

    def restore(self):
        """Restores a soft-deleted user."""
        self.is_active = True
        self.deleted_at = None
        db.session.commit()

    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        """Converts the model instance into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        """Defines how the object is represented as a string."""
        return f"<User {self.username} - {self.role} - {'Active' if self.is_active else 'Inactive'}>"

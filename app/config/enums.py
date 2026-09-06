from enum import Enum


class UserRole(Enum):
    """Add user roles here, when new roles are added, do alembic migrations"""

    USER = "User"
    ADMIN = "Admin"

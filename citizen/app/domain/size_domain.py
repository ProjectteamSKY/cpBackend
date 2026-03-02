import uuid
from datetime import datetime
from typing import Optional


class Size:

    def __init__(
        self,
        name: str,
        width: float,
        height: float,
        unit: str = "mm",
        description: Optional[str] = None,
        is_active: bool = True,
        is_deleted: bool = False,   # ✅ NEW FIELD
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):

        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.width: float = width
        self.height: float = height
        self.unit: str = unit
        self.description: Optional[str] = description
        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted   # ✅ NEW FIELD

        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # ------------------------
    # Active / Inactive
    # ------------------------

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    # ------------------------
    # Soft Delete
    # ------------------------

    def soft_delete(self):
        """Mark size as deleted (soft delete)"""
        self.is_deleted = True
        self.touch()

    def restore(self):
        """Restore soft deleted size"""
        self.is_deleted = False
        self.touch()

    # ------------------------
    # Utility
    # ------------------------

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------
    # Convert to Dict
    # ------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "unit": self.unit,
            "description": self.description,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,   # ✅ INCLUDED
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
import uuid
from datetime import datetime
from typing import Optional


class Subcategory:

    def __init__(
        self,
        category_id: str,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
        is_deleted: bool = False,   # ✅ NEW FIELD
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):

        self.id: str = id or str(uuid.uuid4())
        self.category_id: str = category_id
        self.name: str = name
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
    # Soft Delete Methods
    # ------------------------

    def soft_delete(self):
        """Mark as deleted without removing from DB"""
        self.is_deleted = True
        self.touch()

    def restore(self):
        """Restore soft deleted record"""
        self.is_deleted = False
        self.touch()

    # ------------------------
    # Update Methods
    # ------------------------

    def rename(self, new_name: str):
        if not new_name:
            raise ValueError("Subcategory name cannot be empty")

        self.name = new_name
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------
    # Convert to Dict
    # ------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,   # ✅ INCLUDED
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
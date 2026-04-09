import uuid
from datetime import datetime
from typing import Optional


class AttributeValue:

    def __init__(
        self,
        attribute_id: str,
        value: str,
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: str = id or str(uuid.uuid4())
        self.attribute_id: str = attribute_id
        self.value: str = value.strip()

        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted

        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # ------------------------
    # Status
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
        self.is_deleted = True
        self.touch()

    def restore(self):
        self.is_deleted = False
        self.touch()

    # ------------------------
    # Update
    # ------------------------

    def update_value(self, value: str):
        if not value:
            raise ValueError("Value cannot be empty")
        self.value = value.strip()
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------
    # Dict
    # ------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "attribute_id": self.attribute_id,
            "value": self.value,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
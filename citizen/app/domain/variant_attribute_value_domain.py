import uuid
from datetime import datetime
from typing import Optional


class VariantAttributeValue:

    def __init__(
        self,
        variant_id: str,
        attribute_id: str,
        attribute_value_id: str,
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())

        self.variant_id = variant_id
        self.attribute_id = attribute_id
        self.attribute_value_id = attribute_value_id

        self.is_active = is_active
        self.is_deleted = is_deleted

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # ------------------------
    # State
    # ------------------------

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    def soft_delete(self):
        self.is_deleted = True
        self.touch()

    def restore(self):
        self.is_deleted = False
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "variant_id": self.variant_id,
            "attribute_id": self.attribute_id,
            "attribute_value_id": self.attribute_value_id,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
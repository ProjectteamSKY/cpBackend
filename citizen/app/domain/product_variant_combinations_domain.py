import uuid
from datetime import datetime
from typing import Optional


class ProductVariantCombaination:

    def __init__(
        self,
        product_id: str,
        sku: Optional[str] = None,
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())

        self.product_id = product_id
        self.sku = sku

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
            "product_id": self.product_id,
            "sku": self.sku,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
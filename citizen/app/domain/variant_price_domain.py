import uuid
from datetime import datetime
from typing import Optional


class VariantPrice:
    def __init__(
        self,
        variant_id: str,
        min_qty: int,
        max_qty: Optional[int],
        price: float,
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())

        self.variant_id = variant_id
        self.min_qty = min_qty
        self.max_qty = max_qty
        self.price = price

        self.is_active = is_active
        self.is_deleted = is_deleted

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "variant_id": self.variant_id,
            "min_qty": self.min_qty,
            "max_qty": self.max_qty,
            "price": self.price,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
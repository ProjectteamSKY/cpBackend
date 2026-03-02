import uuid
from datetime import datetime
from typing import Optional


class ProductVariantPrice:

    def __init__(
        self,
        variant_id: str,
        min_qty: int,
        price: float,
        discount_id: Optional[str] = None,
        is_active: bool = True,
        is_deleted: bool = False,   # ✅ NEW FIELD
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.variant_id: str = variant_id
        self.discount_id: Optional[str] = discount_id
        self.min_qty: int = min_qty
        self.price: float = price
        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted   # ✅ NEW FIELD

        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # ---------------------------
    # Active / Inactive
    # ---------------------------

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    # ---------------------------
    # Soft Delete
    # ---------------------------

    def soft_delete(self):
        """Mark price as deleted (soft delete)"""
        self.is_deleted = True
        self.touch()

    def restore(self):
        """Restore soft deleted price"""
        self.is_deleted = False
        self.touch()

    # ---------------------------
    # Domain Methods
    # ---------------------------

    def update_price(self, price: float):
        self.price = price
        self.touch()

    def update_min_qty(self, min_qty: int):
        self.min_qty = min_qty
        self.touch()

    def update_discount(self, discount_id: Optional[str]):
        self.discount_id = discount_id
        self.touch()

    # ---------------------------
    # Utility
    # ---------------------------

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ---------------------------
    # Convert to Dict
    # ---------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "variant_id": self.variant_id,
            "discount_id": self.discount_id,
            "min_qty": self.min_qty,
            "price": self.price,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,   # ✅ INCLUDED
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
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
        custom_qty: bool = False,
        weight: float = 0.0,
        length: float = 0.0,
        breadth: float = 0.0,
        height: float = 0.0,
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
        self.custom_qty = custom_qty

        self.price = float(price)

        self.weight = float(weight or 0.0)
        self.length = float(length or 0.0)
        self.breadth = float(breadth or 0.0)
        self.height = float(height or 0.0)

        self.is_active = is_active
        self.is_deleted = is_deleted

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

        # ✅ VALIDATIONS
        if self.min_qty < 1:
            raise ValueError("min_qty must be >= 1")

        if not self.custom_qty:
            if self.max_qty is None:
                raise ValueError("max_qty required for slab pricing")

            if self.max_qty < self.min_qty:
                raise ValueError("max_qty must be >= min_qty")

        if self.price < 0:
            raise ValueError("price cannot be negative")

        if self.weight < 0:
            raise ValueError("weight cannot be negative")

        for dim in [self.length, self.breadth, self.height]:
            if dim < 0:
                raise ValueError("dimensions cannot be negative")

    # ✅ FIXED (IMPORTANT)
    def to_dict(self):
        return {
            "id": self.id,
            "variant_id": self.variant_id,
            "min_qty": self.min_qty,
            "max_qty": self.max_qty,
            "custom_qty": self.custom_qty,
            "price": self.price,
            "weight": self.weight,
            "length": self.length,
            "breadth": self.breadth,
            "height": self.height,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
        }
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
        weight: float = 0.0,   # ✅ NEW FIELD

        is_active: bool = True,
        is_deleted: bool = False,

        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        # =========================
        # ID
        # =========================
        self.id = id or str(uuid.uuid4())

        # =========================
        # CORE FIELDS
        # =========================
        self.variant_id = variant_id
        self.min_qty = min_qty
        self.max_qty = max_qty
        self.price = float(price)

        # ✅ NEW
        self.weight = float(weight or 0.0)

        # =========================
        # FLAGS
        # =========================
        self.is_active = is_active
        self.is_deleted = is_deleted

        # =========================
        # TIMESTAMPS
        # =========================
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

        # =========================
        # BASIC VALIDATIONS (SAFEGUARD)
        # =========================
        if self.min_qty < 1:
            raise ValueError("min_qty must be >= 1")

        if self.max_qty is not None and self.max_qty < self.min_qty:
            raise ValueError("max_qty must be >= min_qty")

        if self.price < 0:
            raise ValueError("price cannot be negative")

        if self.weight < 0:
            raise ValueError("weight cannot be negative")

    # =========================
    # SERIALIZE
    # =========================
    def to_dict(self):
        return {
            "id": self.id,
            "variant_id": self.variant_id,
            "min_qty": self.min_qty,
            "max_qty": self.max_qty,
            "price": self.price,
            "weight": self.weight,   # ✅ INCLUDED

            "is_active": self.is_active,
            "is_deleted": self.is_deleted,

            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # =========================
    # OPTIONAL: UPDATE HELPER
    # =========================
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

        self.updated_at = datetime.utcnow()
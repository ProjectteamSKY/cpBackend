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
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.variant_id = variant_id
        self.discount_id = discount_id
        self.min_qty = min_qty
        self.price = price
        self.is_active = is_active
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # --------------------------- Domain Methods ---------------------------
    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    def update_price(self, price: float):
        self.price = price
        self.touch()

    def update_min_qty(self, min_qty: int):
        self.min_qty = min_qty
        self.touch()

    def update_discount(self, discount_id: Optional[str]):
        self.discount_id = discount_id
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return self.__dict__
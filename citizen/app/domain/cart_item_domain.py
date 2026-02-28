import uuid
from datetime import datetime
from typing import Optional, Dict


class CartItem:
    def __init__(
        self,
        cart_id: str,
        product_id: str,
        variant_id: str,
        quantity: int = 1,
        unit_price: float = 0,
        total_price: float = 0,
        discount_id: Optional[str] = None,
        selected_options: Optional[Dict] = None,
        status: str = "active",  # active, ordered, cancelled
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: str = id or str(uuid.uuid4())
        self.cart_id: str = cart_id
        self.product_id: str = product_id
        self.variant_id: str = variant_id
        self.quantity: int = quantity
        self.unit_price: float = unit_price
        self.total_price: float = total_price
        self.discount_id: Optional[str] = discount_id
        self.selected_options: Optional[Dict] = selected_options
        self.status: str = status
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return self.__dict__
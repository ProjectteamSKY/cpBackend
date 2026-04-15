import uuid
from datetime import datetime
from typing import Optional, Dict


class CartItem:
    def __init__(
        self,
        cart_id: str,
        product_id: str,
        variant_id: str,
        quantity: int,
        unit_price: float = 0,
        total_price: float = 0,
        variant_price_id: Optional[str] = None,
        discount_id: Optional[str] = None,
        selected_attributes: Optional[Dict] = None,
        status: str = "active",
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.cart_id = cart_id
        self.product_id = product_id
        self.variant_id = variant_id

        self.variant_price_id = variant_price_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price

        self.discount_id = discount_id
        self.selected_attributes = selected_attributes or {}
        self.status = status

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
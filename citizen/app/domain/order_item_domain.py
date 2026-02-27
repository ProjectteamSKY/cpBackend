from typing import Optional
import uuid
from datetime import datetime


class OrderItem:

    def __init__(
        self,
        order_id: str,
        cart_item_id: str,
        product_id: str,
        variant_id: str,
        quantity: int,
        price: float,
        total: float,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: Optional[int] = id
        self.order_id: str = order_id
        self.cart_item_id: str = cart_item_id
        self.product_id: str = product_id
        self.variant_id: str = variant_id
        self.quantity: int = quantity
        self.price: float = price
        self.total: float = total
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "cart_item_id": self.cart_item_id,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "quantity": self.quantity,
            "price": self.price,
            "total": self.total,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
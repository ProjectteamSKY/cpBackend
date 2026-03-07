from typing import Optional
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
        product_variant_price_id: Optional[str] = None,
        customize_qty: Optional[int] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.order_id = order_id
        self.cart_item_id = cart_item_id
        self.product_id = product_id
        self.variant_id = variant_id
        self.product_variant_price_id = product_variant_price_id
        self.customize_qty = customize_qty
        self.quantity = quantity
        self.price = price
        self.total = total
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "cart_item_id": self.cart_item_id,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "product_variant_price_id": self.product_variant_price_id,
            "customize_qty": self.customize_qty,
            "quantity": self.quantity,
            "price": self.price,
            "total": self.total,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
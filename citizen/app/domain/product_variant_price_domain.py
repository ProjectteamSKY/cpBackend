# app/domain/product_variant_price_domain.py
import uuid
from datetime import datetime

class ProductVariantPrice:
    def __init__(
        self,
        variant_id: str,
        min_qty: int,
        max_qty: int,
        price: float,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        is_active: bool = True
    ):
        self.id = id or str(uuid.uuid4())
        self.variant_id = variant_id
        self.min_qty = min_qty
        self.max_qty = max_qty
        self.price = price
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

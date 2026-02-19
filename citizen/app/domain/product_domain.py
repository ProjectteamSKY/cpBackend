# app/domain/product_domain.py
import uuid
from datetime import datetime

class Product:
    def __init__(
        self,
        name: str,
        category_id: str | None = None,
        subcategory_id: str | None = None,
        product_type_id: str | None = None,
        description: str | None = None,
        min_order_qty: int = 100,
        max_order_qty: int | None = None,
        is_active: bool = True,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.product_type_id = product_type_id
        self.description = description
        self.min_order_qty = min_order_qty
        self.max_order_qty = max_order_qty
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

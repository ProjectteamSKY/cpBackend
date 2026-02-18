import uuid
from datetime import datetime

class Product:
    def __init__(
        self,
        name: str,
        category_id: uuid.UUID | None = None,
        subcategory_id: uuid.UUID | None = None,
        product_type_id: uuid.UUID | None = None,
        base_price: float = 0,
        gst_percent: float = 0,
        weight: float = 0,
        length: float = 0,
        width: float = 0,
        height: float = 0,
        min_order_qty: int = 1,
        max_order_qty: int | None = None,
        is_active: bool = True,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None
    ):
        self.id = id or uuid.uuid4()
        self.name = name
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.product_type_id = product_type_id
        self.base_price = base_price
        self.gst_percent = gst_percent
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        self.min_order_qty = min_order_qty
        self.max_order_qty = max_order_qty
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.variants = []
        self.images = []

    def __repr__(self):
        return f"<Product id={self.id} name={self.name}>"

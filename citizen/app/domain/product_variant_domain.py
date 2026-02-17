import uuid
from datetime import datetime
from typing import Optional

class ProductVariant:
    """Specific variant of a product including size, paper type, finish, cut type, price, sides, and orientation."""

    def __init__(
        self,
        product_id: str,
        price: float,
        size: str | None = None,
        paper_type_id: str | None = None,
        finish_id: str | None = None,
        cut_type_id: str | None = None,
        sides: int = 1,
        orientation: str = "Portrait",
        is_active: bool = True,
        id: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.product_id = product_id
        self.paper_type_id = paper_type_id
        self.finish_id = finish_id
        self.cut_type_id = cut_type_id
        self.size = size
        self.sides = sides
        self.orientation = orientation
        self.price = price
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

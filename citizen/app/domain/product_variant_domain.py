import uuid
from datetime import datetime

class ProductVariant:
    def __init__(
        self,
        product_id: str,
        paper_type_id: str | None = None,
        finish_id: str | None = None,
        cut_type_id: str | None = None,
        shape_id: str | None = None,
        size_id: str | None = None, 
        sides: int | None = None,
        two_side_cut: bool = False,
        four_side_cut: bool = False,
        orientation: str = "Portrait",
        is_active: bool = True,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ):
        self.id = id or str(uuid.uuid4())
        self.product_id = product_id
        self.paper_type_id = paper_type_id
        self.finish_id = finish_id
        self.cut_type_id = cut_type_id
        self.shape_id = shape_id
        self.size_id = size_id
        self.sides = sides
        self.two_side_cut = two_side_cut
        self.four_side_cut = four_side_cut
        self.orientation = orientation
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

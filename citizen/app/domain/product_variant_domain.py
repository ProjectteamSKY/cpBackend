import uuid
from datetime import datetime
from typing import Optional

class ProductVariant:
    def __init__(
        self,
        product_id: str,
        size_id: str,
        paper_type_id: Optional[str] = None,
        print_type_id: Optional[str] = None,
        cut_type_id: Optional[str] = None,
        sides: Optional[int] = None,
        two_side_cut: bool = False,
        four_side_cut: bool = False,
        orientation: str = "Portrait",
        is_active: bool = True,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.product_id = product_id
        self.size_id = size_id
        self.paper_type_id = paper_type_id
        self.print_type_id = print_type_id
        self.cut_type_id = cut_type_id
        self.sides = sides
        self.two_side_cut = two_side_cut
        self.four_side_cut = four_side_cut
        self.orientation = orientation
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "size_id": self.size_id,
            "paper_type_id": self.paper_type_id,
            "print_type_id": self.print_type_id,
            "cut_type_id": self.cut_type_id,
            "sides": self.sides,
            "two_side_cut": self.two_side_cut,
            "four_side_cut": self.four_side_cut,
            "orientation": self.orientation,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
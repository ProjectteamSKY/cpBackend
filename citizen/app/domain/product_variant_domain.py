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
        is_deleted: bool = False,   # ✅ NEW FIELD
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: str = id or str(uuid.uuid4())
        self.product_id: str = product_id
        self.size_id: str = size_id
        self.paper_type_id: Optional[str] = paper_type_id
        self.print_type_id: Optional[str] = print_type_id
        self.cut_type_id: Optional[str] = cut_type_id
        self.sides: Optional[int] = sides
        self.two_side_cut: bool = two_side_cut
        self.four_side_cut: bool = four_side_cut
        self.orientation: str = orientation
        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted   # ✅ NEW FIELD

        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # ------------------------
    # Active / Inactive
    # ------------------------

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    # ------------------------
    # Soft Delete
    # ------------------------

    def soft_delete(self):
        """Mark product variant as deleted (soft delete)"""
        self.is_deleted = True
        self.touch()

    def restore(self):
        """Restore soft deleted product variant"""
        self.is_deleted = False
        self.touch()

    # ------------------------
    # Utility
    # ------------------------

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------
    # Convert to Dict
    # ------------------------

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
            "is_deleted": self.is_deleted,   # ✅ INCLUDED
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
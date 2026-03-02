import uuid
from datetime import datetime
from typing import Optional, List, Dict


class Product:

    def __init__(
        self,
        name: str,
        category_id: Optional[str] = None,
        subcategory_id: Optional[str] = None,
        description: Optional[str] = None,
        min_order_qty: int = 100,
        max_order_qty: Optional[int] = None,
        images: Optional[List[Dict]] = None,
        related_images: Optional[List[Dict]] = None,
        is_active: bool = True,
        is_deleted: bool = False,   # ✅ NEW FIELD
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.category_id: Optional[str] = category_id
        self.subcategory_id: Optional[str] = subcategory_id
        self.name: str = name
        self.description: Optional[str] = description
        self.min_order_qty: int = min_order_qty
        self.max_order_qty: Optional[int] = max_order_qty
        self.images: List[Dict] = images or []
        self.related_images: List[Dict] = related_images or []
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
        """Mark product as deleted (soft delete)"""
        self.is_deleted = True
        self.touch()

    def restore(self):
        """Restore soft deleted product"""
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
            "category_id": self.category_id,
            "subcategory_id": self.subcategory_id,
            "name": self.name,
            "description": self.description,
            "min_order_qty": self.min_order_qty,
            "max_order_qty": self.max_order_qty,
            "images": self.images,
            "related_images": self.related_images,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,   # ✅ INCLUDED
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
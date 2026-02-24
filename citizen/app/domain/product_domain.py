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
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.name = name
        self.description = description
        self.min_order_qty = min_order_qty
        self.max_order_qty = max_order_qty
        self.images = images or []
        self.related_images = related_images or []
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
            "category_id": self.category_id,
            "subcategory_id": self.subcategory_id,
            "name": self.name,
            "description": self.description,
            "min_order_qty": self.min_order_qty,
            "max_order_qty": self.max_order_qty,
            "images": self.images,
            "related_images": self.related_images,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
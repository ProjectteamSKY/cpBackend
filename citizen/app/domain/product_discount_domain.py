import uuid
from datetime import datetime
from typing import Optional

class ProductDiscount:
    def __init__(
        self,
        product_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        discount: str = "0%",
        banner_image_url: Optional[str] = None,
        cta_text: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_active: bool = True,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.product_id = product_id
        self.title = title
        self.description = description
        self.discount = discount
        self.banner_image_url = banner_image_url
        self.cta_text = cta_text
        self.start_date = start_date or datetime.utcnow()
        self.end_date = end_date or datetime.utcnow()
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
            "title": self.title,
            "description": self.description,
            "discount": self.discount,
            "banner_image_url": self.banner_image_url,
            "cta_text": self.cta_text,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
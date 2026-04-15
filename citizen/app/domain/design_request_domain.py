import datetime
from typing import List, Optional
import uuid


class DesignRequest:

    def __init__(
        self,
        user_id: str,
        name: str,
        phone: str,

        email: Optional[str] = None,

        product_id: Optional[str] = None,
        product_name: Optional[str] = None,

        variant_id: Optional[str] = None,
        variant_price_id: Optional[str] = None,
        selected_attributes: Optional[dict] = None,

        design_notes: Optional[str] = None,

        logo_images: Optional[List[str]] = None,
        designed_images: Optional[List[str]] = None,

        status: str = "NEW",
        is_approved: bool = False,
        design_price: Optional[float] = None,

        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())

        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email

        self.product_id = product_id
        self.product_name = product_name

        self.variant_id = variant_id
        self.variant_price_id = variant_price_id
        self.selected_attributes = selected_attributes or {}

        self.design_notes = design_notes

        self.logo_images = logo_images or []
        self.designed_images = designed_images or []

        self.status = status
        self.is_approved = is_approved
        self.design_price = design_price

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,

            "product_id": self.product_id,
            "product_name": self.product_name,

            "variant_id": self.variant_id,
            "variant_price_id": self.variant_price_id,
            "selected_attributes": self.selected_attributes,

            "design_notes": self.design_notes,

            "logo_images": self.logo_images,
            "designed_images": self.designed_images,

            "status": self.status,
            "is_approved": self.is_approved,
            "design_price": self.design_price,

            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
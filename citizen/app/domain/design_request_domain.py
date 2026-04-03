import uuid
from datetime import datetime
from typing import Optional, List


class DesignRequest:

    def __init__(
        self,
        user_id: str,
        name: str,
        phone: str,
        email: Optional[str] = None,

        product_id: Optional[str] = None,
        product_name: Optional[str] = None,

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

        self.design_notes = design_notes

        self.logo_images = logo_images or []
        self.designed_images = designed_images or []

        self.status = status
        self.is_approved = is_approved
        self.design_price = design_price

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # ------------------------
    # Status Handling
    # ------------------------

    def update_status(self, status: str):
        self.status = status
        self.touch()

    def approve(self):
        self.is_approved = True
        self.status = "APPROVED"
        self.touch()

    def reject(self):
        self.is_approved = False
        self.status = "REJECTED"
        self.touch()

    # ------------------------
    # Image Handling
    # ------------------------

    def add_designed_images(self, images: List[str]):
        self.designed_images.extend(images)
        self.touch()

    # ------------------------
    # Common
    # ------------------------

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,

            "name": self.name,
            "phone": self.phone,
            "email": self.email,

            "product_id": self.product_id,
            "product_name": self.product_name,

            "design_notes": self.design_notes,

            "logo_images": self.logo_images,
            "designed_images": self.designed_images,

            "status": self.status,
            "is_approved": self.is_approved,
            "design_price": self.design_price,

            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
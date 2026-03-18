import uuid
from datetime import datetime
from typing import Optional

class CustomerReview:

    def __init__(
        self,
        product_id: str,
        user_id: str,
        rating: float,
        customer_name: Optional[str] = None,
        comment: Optional[str] = None,
        image_url: Optional[str] = None,
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: str = id or str(uuid.uuid4())
        self.product_id: str = product_id
        self.user_id: str = user_id
        self.customer_name: Optional[str] = customer_name
        self.rating: float = rating
        self.comment: Optional[str] = comment
        self.image_url: Optional[str] = image_url
        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted
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
        self.is_deleted = True
        self.touch()

    def restore(self):
        self.is_deleted = False
        self.touch()

    # ------------------------
    # Update
    # ------------------------
    def update_comment(self, comment: str):
        self.comment = comment
        self.touch()

    def update_rating(self, rating: float):
        if rating < 1.0 or rating > 5.0:
            raise ValueError("Rating must be between 1 and 5")
        self.rating = rating
        self.touch()

    def update_image(self, image_url: str):
        self.image_url = image_url
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------
    # Convert to Dict
    # ------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "customer_name": self.customer_name,
            "rating": self.rating,
            "comment": self.comment,
            "image_url": self.image_url,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # ------------------------
    # Stars representation
    # ------------------------
    def stars(self):
        full_stars = int(self.rating)
        half_star = 1 if self.rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return "⭐" * full_stars + ("✰" if half_star else "") + "☆" * empty_stars
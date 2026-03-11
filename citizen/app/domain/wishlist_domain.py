import uuid
from datetime import datetime
from typing import Optional


class Wishlist:
    def __init__(
        self,
        user_id: str,
        product_id: str,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.user_id: str = user_id
        self.product_id: str = product_id
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
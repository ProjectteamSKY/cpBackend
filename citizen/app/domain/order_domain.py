import uuid
from datetime import datetime
from typing import Optional


class Order:

    def __init__(
        self,
        user_id: str,
        cart_id: str,
        total_amount: float,
        address_id: Optional[str] = None,
        status: str = "pending",
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: str = id or str(uuid.uuid4())
        self.user_id: str = user_id
        self.cart_id: str = cart_id
        self.address_id: Optional[str] = address_id
        self.status: str = status
        self.total_amount: float = total_amount
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "cart_id": self.cart_id,
            "address_id": self.address_id,
            "status": self.status,
            "total_amount": self.total_amount,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
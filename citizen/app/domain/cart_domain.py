import uuid
from datetime import datetime
from typing import Optional


class Cart:
    def __init__(
        self,
        user_id: str,
        status: str = "active",
        total_amount: float = 0,
        total_discount: float = 0,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: str = id or str(uuid.uuid4())
        self.user_id: str = user_id
        self.status: str = status
        self.total_amount: float = total_amount
        self.total_discount: float = total_discount
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return self.__dict__
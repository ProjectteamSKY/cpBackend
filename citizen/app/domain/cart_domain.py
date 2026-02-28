import uuid
from datetime import datetime


class Cart:
    def __init__(
        self,
        user_id: str,
        status: str = "active",
        total_amount: float = 0,
        total_discount: float = 0
    ):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.status = status
        self.total_amount = total_amount
        self.total_discount = total_discount
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return self.__dict__
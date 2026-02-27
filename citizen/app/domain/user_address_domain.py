import uuid
from datetime import datetime
from typing import Optional


class UserAddress:

    def __init__(
        self,
        user_id: str,
        address: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        phone: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.user_id: str = user_id
        self.address: str = address
        self.city: Optional[str] = city
        self.state: Optional[str] = state
        self.country: Optional[str] = country
        self.postal_code: Optional[str] = postal_code
        self.phone: Optional[str] = phone
        self.created_at: datetime = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "phone": self.phone,
            "created_at": self.created_at,
        }
import uuid
from datetime import datetime


class User:

    def __init__(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        phone: str | None = None,
        id: uuid.String | None = None,
        is_active: bool = True,
        is_verified: bool = False,
        created_at: datetime | None = None,
    ):
        self.id = id or uuid.uuid4()
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.phone = phone
        self.is_active = is_active
        self.is_verified = is_verified
        self.created_at = created_at or datetime.utcnow()

    # Business logic inside domain
    def verify(self):
        self.is_verified = True

    def deactivate(self):
        self.is_active = False

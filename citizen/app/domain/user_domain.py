import uuid
from datetime import datetime


class User:
    def __init__(
        self,
        full_name: str,
        email: str,
        password: str,
        contact: str | None = None,
        id: str | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
    ):
        self.id = id or str(uuid.uuid4())  # ✅ UUID GENERATED HERE
        self.full_name = full_name
        self.email = email
        self.password = password
        self.contact = contact
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

    def deactivate(self):
        self.is_active = False
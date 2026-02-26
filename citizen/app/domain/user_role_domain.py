import uuid
from datetime import datetime


class UserRole:
    def __init__(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str | None = None,
        id: str | None = None,
        assigned_at: datetime | None = None,
    ):
        self.id = id or str(uuid.uuid4())  # UUID generated here
        self.user_id = user_id
        self.role_id = role_id
        self.assigned_by = assigned_by
        self.assigned_at = assigned_at or datetime.utcnow()
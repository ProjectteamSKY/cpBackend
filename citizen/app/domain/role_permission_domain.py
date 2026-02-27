import uuid
from datetime import datetime


class RolePermission:
    def __init__(
        self,
        role_id: str,
        permission_id: str,
        id: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id or str(uuid.uuid4())  # UUID generated here
        self.role_id = role_id
        self.permission_id = permission_id
        self.created_at = created_at or datetime.utcnow()
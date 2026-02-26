import uuid
from datetime import datetime


class Permission:
    def __init__(
        self,
        resource_id: str,
        action: str,
        method: str,
        path: str,
        description: str | None = None,
        id: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id or str(uuid.uuid4())  # ✅ UUID GENERATED HERE
        self.resource_id = resource_id
        self.action = action
        self.method = method
        self.path = path
        self.description = description
        self.created_at = created_at or datetime.utcnow()
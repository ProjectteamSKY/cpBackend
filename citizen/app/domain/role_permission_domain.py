import uuid
from datetime import datetime
from typing import Optional

class RolePermission:
    def __init__(
        self,
        role_id: str,
        permission_id: str,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.role_id: str = role_id
        self.permission_id: str = permission_id
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "permission_id": self.permission_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
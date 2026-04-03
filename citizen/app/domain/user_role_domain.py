import uuid
from datetime import datetime
from typing import Optional

class UserRole:
    def __init__(
        self,
        user_id: str,
        role_id: str,
        assigned_by: Optional[str] = None,
        assigned_at: Optional[datetime] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.user_id: str = user_id
        self.role_id: str = role_id
        self.assigned_by: Optional[str] = assigned_by
        self.assigned_at: datetime = assigned_at or datetime.utcnow()
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "assigned_by": self.assigned_by,
            "assigned_at": self.assigned_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
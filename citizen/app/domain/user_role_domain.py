from datetime import datetime
from typing import Optional

class UserRole:
    def __init__(
        self,
        user_id: int,
        role_id: int,
        assigned_by: Optional[int] = None,
        assigned_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.role_id = role_id
        self.assigned_by = assigned_by
        self.assigned_at = assigned_at or datetime.utcnow()
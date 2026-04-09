import uuid
from datetime import datetime
from typing import Optional

class Permission:
    def __init__(
        self,
        resource_id: Optional[str],
        action: str,
        method: str,
        path: str,
        description: Optional[str] = None,
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id: str = id or str(uuid.uuid4())
        self.resource_id: Optional[str] = resource_id
        self.action: str = action
        self.method: str = method
        self.path: str = path
        self.description: Optional[str] = description
        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # ------------------------ #
    # Active / Inactive
    # ------------------------ #
    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    # ------------------------ #
    # Soft Delete
    # ------------------------ #
    def soft_delete(self):
        self.is_deleted = True
        self.touch()

    def restore(self):
        self.is_deleted = False
        self.touch()

    # ------------------------ #
    # Update Methods
    # ------------------------ #
    def update(self, action=None, method=None, path=None, description=None, resource_id=None):
        if action is not None:
            self.action = action
        if method is not None:
            self.method = method
        if path is not None:
            self.path = path
        if description is not None:
            self.description = description
        if resource_id is not None:
            self.resource_id = resource_id
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------ #
    # Convert to Dict
    # ------------------------ #
    def to_dict(self):
        return {
            "id": self.id,
            "resource_id": self.resource_id,
            "action": self.action,
            "method": self.method,
            "path": self.path,
            "description": self.description,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
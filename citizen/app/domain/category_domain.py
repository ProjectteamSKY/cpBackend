import uuid
from datetime import datetime
from typing import Optional


class Category:

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):

        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.description: Optional[str] = description
        self.is_active: bool = is_active
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    def rename(self, new_name: str):
        if not new_name:
            raise ValueError("Category name cannot be empty")
        self.name = new_name
        self.touch()

    def update_description(self, description: Optional[str]):
        self.description = description
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
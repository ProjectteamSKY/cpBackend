import uuid
from datetime import datetime
from typing import Optional



class PaperType:
    def __init__(
        self,
        name: str,
        gsm: float = 300,
        description: Optional[str] = None,
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.gsm: float = gsm
        self.description: Optional[str] = description
        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # ------------------------
    # Active / Inactive
    # ------------------------
    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    # ------------------------
    # Soft Delete
    # ------------------------
    def soft_delete(self):
        self.is_deleted = True
        self.touch()

    def restore(self):
        self.is_deleted = False
        self.touch()

    # ------------------------
    # Update Methods
    # ------------------------
    def rename(self, new_name: str):
        if not new_name:
            raise ValueError("Paper type name cannot be empty")
        self.name = new_name
        self.touch()

    def update_description(self, description: Optional[str]):
        self.description = description
        self.touch()

    def update_gsm(self, gsm: float):
        if gsm <= 0:
            raise ValueError("GSM must be greater than 0")
        self.gsm = gsm
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------
    # Convert to Dict
    # ------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gsm": self.gsm,
            "description": self.description,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

import uuid
from datetime import datetime
from typing import Optional


class ProductType:

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, name: Optional[str], description: Optional[str]):
        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        self.updated_at = datetime.utcnow()

    def deactivate(self):
        self.is_active = False
        self.updated_at = datetime.utcnow()

import uuid
from datetime import datetime

class Category:
    def __init__(self, name: str, description: str | None = None,
                 is_active: bool = True, id: uuid.UUID | None = None,
                 created_at: datetime | None = None):
        self.id = id or uuid.uuid4()
        self.name = name
        self.description = description
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
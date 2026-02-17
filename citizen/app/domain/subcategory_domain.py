import uuid
from datetime import datetime

class SubCategory:
    def __init__(self, name: str, category_id: uuid.UUID, description: str | None = None, is_active: bool = True,
                 id: uuid.UUID | None = None, created_at: datetime | None = None):
        self.id = id or uuid.uuid4()
        self.category_id = category_id
        self.name = name
        self.description = description
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

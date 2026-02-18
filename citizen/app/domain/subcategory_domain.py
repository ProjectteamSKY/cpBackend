import uuid
from datetime import datetime

class SubCategory:
    def __init__(
        self,
        name: str,
        category_id: str,
        description: str | None = None,
        is_active: bool = True,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.category_id = category_id
        self.description = description
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

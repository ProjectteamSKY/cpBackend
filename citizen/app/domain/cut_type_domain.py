import uuid
from datetime import datetime

class CutType:
    """Stores available cut types for products, e.g., Die Cut, Straight Cut, Rounded Corner."""
    
    def __init__(
        self,
        name: str,
        description: str | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None
    ):
        self.id = id or uuid.uuid4()
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()

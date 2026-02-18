import uuid
from datetime import datetime

class Finish:
    def __init__(
        self,
        name: str,
        description: str | None = None,
        id: str | None = None,
        created_at: datetime | None = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()

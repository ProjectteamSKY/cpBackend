from datetime import datetime
import uuid

class PaperType:
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

    def __repr__(self):
        return f"<PaperType id={self.id} name={self.name}>"

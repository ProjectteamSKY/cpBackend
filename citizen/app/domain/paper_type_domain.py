import uuid
from datetime import datetime


class PaperType:

    def __init__(
        self,
        name: str,
        description: str | None = None,
        id: str | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ):
        self.id = id or str(uuid.uuid4())

        self.name = name
        self.description = description

        self.is_active = is_active

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self):
        return f"<PaperType id={self.id} name={self.name}>"

import uuid
from datetime import datetime

class SheetTemplate:
    """Defines sheet size and layout info to calculate how many cards fit per sheet."""

    def __init__(
        self,
        sheet_type: str,
        card_width: float,
        card_height: float,
        max_cards_per_sheet: int,
        id: str | None = None,
        created_at: datetime | None = None
    ):
        self.id = id or str(uuid.uuid4())
        self.sheet_type = sheet_type
        self.card_width = card_width
        self.card_height = card_height
        self.max_cards_per_sheet = max_cards_per_sheet
        self.created_at = created_at or datetime.utcnow()

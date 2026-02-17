from pydantic import BaseModel
from uuid import UUID

class SheetTemplateCreateSchema(BaseModel):
    sheet_type: str
    card_width: float
    card_height: float
    max_cards_per_sheet: int

class SheetTemplateResponseSchema(BaseModel):
    id: UUID
    sheet_type: str
    card_width: float
    card_height: float
    max_cards_per_sheet: int

    class Config:
        from_attributes = True

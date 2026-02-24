from pydantic import BaseModel

class SheetTemplateCreateSchema(BaseModel):
    sheet_type: str
    card_width: float
    card_height: float
    max_cards_per_sheet: int

class SheetTemplateResponseSchema(BaseModel):
    id: str
    sheet_type: str
    card_width: float
    card_height: float
    max_cards_per_sheet: int

    class Config:
        from_attributes = True

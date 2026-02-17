from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class PaperTypeCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class PaperTypeResponseSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

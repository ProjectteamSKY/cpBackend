from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CutTypeCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class CutTypeResponseSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

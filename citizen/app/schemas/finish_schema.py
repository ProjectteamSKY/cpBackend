from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class FinishCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class FinishResponseSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

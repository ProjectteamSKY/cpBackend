from pydantic import BaseModel
from typing import Optional

class CutTypeCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class CutTypeResponseSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

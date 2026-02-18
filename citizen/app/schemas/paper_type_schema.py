from pydantic import BaseModel
from typing import Optional

class PaperTypeCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class PaperTypeResponseSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

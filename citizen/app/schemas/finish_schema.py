from pydantic import BaseModel
from typing import Optional

class FinishCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class FinishResponseSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

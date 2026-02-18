from pydantic import BaseModel
from typing import Optional

class ProductTypeCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class ProductTypeResponseSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

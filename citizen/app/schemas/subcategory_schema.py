from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SubCategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: UUID
    is_active: Optional[bool] = True

class SubCategoryResponseSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category_id: UUID
    is_active: bool

    class Config:
        from_attributes = True

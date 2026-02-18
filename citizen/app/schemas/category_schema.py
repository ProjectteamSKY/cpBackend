# app/schemas/category_schema.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponseSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

# app/schemas/custom_shape_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomShapeCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None

class CustomShapeUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]

class CustomShapeResponseSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# app/schemas/product_image_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductrelatedImageCreateSchema(BaseModel):
    product_id: str
    is_default: Optional[bool] = False

class ProductrelatedImageResponseSchema(BaseModel):
    id: str
    product_id: str
    image_url: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

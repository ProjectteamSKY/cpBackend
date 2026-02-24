# app/schemas/product_variant_price_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductVariantPriceCreateSchema(BaseModel):
    variant_id: str
    min_qty: int
    max_qty: int
    price: float

class ProductVariantPriceUpdateSchema(BaseModel):
    min_qty: Optional[int]
    max_qty: Optional[int]
    price: Optional[float]

class ProductVariantPriceResponseSchema(BaseModel):
    id: str
    variant_id: str
    min_qty: int
    max_qty: int
    price: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

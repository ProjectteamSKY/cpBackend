from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductImageResponseSchema(BaseModel):
    id: str
    image_url: str
    is_default: bool

class ProductResponseSchema(BaseModel):
    id: str
    name: str
    category_id: str
    subcategory_id: str
    product_type_id: str
    description: Optional[str] = None
    min_order_qty: int
    max_order_qty: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: Optional[List[ProductImageResponseSchema]] = []  # NEW: include images

    class Config:
        orm_mode = True

class ProductCreateSchema(BaseModel):
    name: str
    category_id: str
    subcategory_id: str
    product_type_id: str
    description: Optional[str] = None
    min_order_qty: Optional[int] = 100
    max_order_qty: Optional[int] = None

class ProductUpdateSchema(BaseModel):
    name: Optional[str]
    category_id: Optional[str]
    subcategory_id: Optional[str]
    product_type_id: Optional[str]
    description: Optional[str]
    min_order_qty: Optional[int]
    max_order_qty: Optional[int]

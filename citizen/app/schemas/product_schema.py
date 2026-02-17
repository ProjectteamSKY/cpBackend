from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class ProductCreateSchema(BaseModel):
    name: str
    category_id: Optional[UUID] = None
    subcategory_id: Optional[UUID] = None
    product_type_id: Optional[UUID] = None
    base_price: float = 0
    gst_percent: float = 0
    weight: float = 0
    length: float = 0
    width: float = 0
    height: float = 0
    min_order_qty: int = 1
    max_order_qty: Optional[int] = None
    is_active: Optional[bool] = True

class ProductResponseSchema(BaseModel):
    id: UUID
    name: str
    category_id: Optional[UUID]
    subcategory_id: Optional[UUID]
    product_type_id: Optional[UUID]
    base_price: float
    gst_percent: float
    weight: float
    length: float
    width: float
    height: float
    min_order_qty: int
    max_order_qty: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True

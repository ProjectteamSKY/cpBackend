from pydantic import BaseModel
from typing import Optional, List

class ProductCreateSchema(BaseModel):
    name: str
    category_id: Optional[str] = None
    subcategory_id: Optional[str] = None
    product_type_id: Optional[str] = None
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
    id: str
    name: str
    category_id: Optional[str]
    subcategory_id: Optional[str]
    product_type_id: Optional[str]
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

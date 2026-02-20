from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Discount(BaseModel):
    id: Optional[str]
    description: str
    discount: str
    start_date: datetime
    end_date: datetime

class Price(BaseModel):
    id: Optional[str]
    min_qty: int
    max_qty: int
    price: float
    discount: Optional[Discount]

class Variant(BaseModel):
    id: Optional[str]
    size_id: str
    paper_type_id: Optional[str]
    print_type_id: Optional[str]
    cut_type_id: Optional[str]
    sides: Optional[int] = 1
    two_side_cut: Optional[bool] = False
    four_side_cut: Optional[bool] = False
    orientation: Optional[str] = "Portrait"
    prices: Optional[List[Price]] = []

class ProductSetup(BaseModel):
    product_id: Optional[str]
    category_id: Optional[str]
    subcategory_id: Optional[str]
    name: str
    description: Optional[str]
    min_order_qty: Optional[int] = 100
    max_order_qty: Optional[int]
    images: Optional[List[str]] = []
    related_images: Optional[List[str]] = []
    variants: Optional[List[Variant]] = []
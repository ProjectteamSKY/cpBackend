from pydantic import BaseModel
from typing import Optional

class ProductVariantCreateSchema(BaseModel):
    product_id: str
    paper_type_id: Optional[str] = None
    finish_id: Optional[str] = None
    cut_type_id: Optional[str] = None
    size: Optional[str] = None
    sides: int = 1
    orientation: str = "Portrait"
    price: float
    is_active: Optional[bool] = True

class ProductVariantResponseSchema(BaseModel):
    id: str
    product_id: str
    paper_type_id: Optional[str]
    finish_id: Optional[str]
    cut_type_id: Optional[str]
    size: Optional[str]
    sides: int
    orientation: str
    price: float
    is_active: bool

    class Config:
        from_attributes = True

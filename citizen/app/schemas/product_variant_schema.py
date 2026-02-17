from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProductVariantCreateSchema(BaseModel):
    product_id: UUID
    paper_type_id: Optional[UUID] = None
    finish_id: Optional[UUID] = None
    cut_type_id: Optional[UUID] = None
    size: Optional[str] = None
    sides: int = 1
    orientation: str = "Portrait"
    price: float
    is_active: Optional[bool] = True

class ProductVariantResponseSchema(BaseModel):
    id: UUID
    product_id: UUID
    paper_type_id: Optional[UUID]
    finish_id: Optional[UUID]
    cut_type_id: Optional[UUID]
    size: Optional[str]
    sides: int
    orientation: str
    price: float
    is_active: bool

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductVariantCreateSchema(BaseModel):
    product_id: str
    paper_type_id: Optional[str]
    finish_id: Optional[str]
    cut_type_id: Optional[str]
    shape_id: Optional[str]
    size_id: Optional[str]
    sides: Optional[int]
    two_side_cut: Optional[bool] = False
    four_side_cut: Optional[bool] = False
    orientation: Optional[str] = "Portrait"

class ProductVariantUpdateSchema(BaseModel):
    paper_type_id: Optional[str]
    finish_id: Optional[str]
    cut_type_id: Optional[str]
    shape_id: Optional[str]
    size_id: Optional[str]
    sides: Optional[int]
    two_side_cut: Optional[bool]
    four_side_cut: Optional[bool]
    orientation: Optional[str]

class ProductVariantResponseSchema(BaseModel):
    id: str
    product_id: str
    paper_type_id: Optional[str]
    finish_id: Optional[str]
    cut_type_id: Optional[str]
    shape_id: Optional[str]
    size_id: Optional[str]
    sides: Optional[int]
    two_side_cut: bool
    four_side_cut: bool
    orientation: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

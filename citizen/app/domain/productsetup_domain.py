from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# =====================================================
# Image Models
# =====================================================

class ProductImage(BaseModel):
    id: str
    url: str
    is_default: bool = False


class RelatedImage(BaseModel):
    id: str
    url: str


# =====================================================
# Discount Model
# =====================================================

class Discount(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    discount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator("discount")
    @classmethod
    def validate_discount(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Discount must be between 0 and 100")
        return v


# =====================================================
# Price Model
# =====================================================

class Price(BaseModel):
    id: Optional[str] = None
    min_qty: int
    max_qty: int
    price: float
    discount: Optional[Discount] = None

    @field_validator("max_qty")
    @classmethod
    def validate_quantity_range(cls, v, info):
        min_qty = info.data.get("min_qty")
        if min_qty is not None and v < min_qty:
            raise ValueError("max_qty must be greater than or equal to min_qty")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


# =====================================================
# Variant Model
# =====================================================

class Variant(BaseModel):
    id: Optional[str] = None
    size_id: str
    paper_type_id: Optional[str] = None
    print_type_id: Optional[str] = None
    cut_type_id: Optional[str] = None
    sides: int = 1
    two_side_cut: bool = False
    four_side_cut: bool = False
    orientation: str = "Portrait"

    prices: List[Price] = Field(default_factory=list)

    @field_validator("sides")
    @classmethod
    def validate_sides(cls, v):
        if v not in [1, 2]:
            raise ValueError("Sides must be either 1 or 2")
        return v


# =====================================================
# Product Setup Model
# =====================================================

class ProductSetup(BaseModel):
    product_id: Optional[str] = None
    category_id: Optional[str] = None
    subcategory_id: Optional[str] = None

    name: str
    description: Optional[str] = None

    min_order_qty: int = 100
    max_order_qty: Optional[int] = None

    images: List[ProductImage] = Field(default_factory=list)
    related_images: List[RelatedImage] = Field(default_factory=list)

    variants: List[Variant] = Field(default_factory=list)

    @field_validator("max_order_qty")
    @classmethod
    def validate_order_range(cls, v, info):
        min_qty = info.data.get("min_order_qty")
        if v is not None and min_qty is not None and v < min_qty:
            raise ValueError("max_order_qty must be greater than min_order_qty")
        return v
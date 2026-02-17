from pydantic import BaseModel
from uuid import UUID

class ProductImageCreateSchema(BaseModel):
    product_id: UUID
    image_url: str
    is_default: bool = False

class ProductImageResponseSchema(BaseModel):
    id: UUID
    product_id: UUID
    image_url: str
    is_default: bool

    class Config:
        from_attributes = True

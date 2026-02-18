from pydantic import BaseModel

class ProductImageCreateSchema(BaseModel):
    product_id: str
    image_url: str
    is_default: bool = False

class ProductImageResponseSchema(BaseModel):
    id: str
    product_id: str
    image_url: str
    is_default: bool

    class Config:
        from_attributes = True

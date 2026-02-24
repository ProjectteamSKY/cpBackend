from pydantic import BaseModel
from typing import Optional

class SubCategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: str
    is_active: Optional[bool] = True

class SubCategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = None

class SubCategoryResponseSchema(BaseModel): 
    id: str
    name: str
    description: Optional[str]
    category_id: str
    is_active: bool

    class Config:
        from_attributes = True

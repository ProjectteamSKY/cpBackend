from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaperTypeCreateSchema(BaseModel):

    name: str
    description: Optional[str] = None


class PaperTypeUpdateSchema(BaseModel):

    name: Optional[str] = None
    description: Optional[str] = None


class PaperTypeResponseSchema(BaseModel):

    id: str
    name: str
    description: Optional[str]

    is_active: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

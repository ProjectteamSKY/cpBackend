from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FinishCreateSchema(BaseModel):

    name: str

    description: Optional[str] = None


class FinishUpdateSchema(BaseModel):

    name: Optional[str] = None

    description: Optional[str] = None


class FinishResponseSchema(BaseModel):

    id: str

    name: str

    description: Optional[str]

    is_active: bool

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True

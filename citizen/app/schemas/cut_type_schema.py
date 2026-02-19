from datetime import datetime
from pydantic import BaseModel


class CutTypeCreate(BaseModel):
    name: str
    description: str | None = None


class CutTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class CutTypeResponse(BaseModel):
    id: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.attributes_domain import Attribute
from app.services.attribute_service import *

router = APIRouter()


class AttributeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class AttributeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/create")
async def create_attribute_endpoint(payload: AttributeCreate):
    attr = Attribute(**payload.model_dump())
    return {"status": "success", "data": await create_attribute(attr)}


@router.get("/list")
async def list_attributes():
    return {"status": "success", "data": await get_all_attributes()}


@router.get("/{id}")
async def get_attribute_endpoint(id: str):
    data = await get_attribute_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return {"status": "success", "data": data}


@router.put("/{id}")
async def update_attribute_endpoint(id: str, payload: AttributeUpdate):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    data = await update_attribute(id, updates)
    if not data:
        raise HTTPException(status_code=404, detail="Attribute not found")

    return {"status": "success", "data": data}


@router.delete("/{id}")
async def delete_attribute_endpoint(id: str):
    result = await delete_attribute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Attribute not found")

    return {"status": "success", "deleted_id": id}


@router.put("/{id}/activate")
async def activate_attribute_endpoint(id: str):
    return {"status": "success", "data": await activate_attribute(id)}


@router.put("/{id}/deactivate")
async def deactivate_attribute_endpoint(id: str):
    return {"status": "success", "data": await deactivate_attribute(id)}
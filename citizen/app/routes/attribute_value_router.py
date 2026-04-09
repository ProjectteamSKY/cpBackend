from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.attribute_value_domain import AttributeValue
from app.services.attribute_value_service import *

router = APIRouter()


class AttributeValueCreate(BaseModel):
    attribute_id: str
    value: str
    is_active: bool = True


class AttributeValueUpdate(BaseModel):
    value: Optional[str] = None
    is_active: Optional[bool] = None


# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_attribute_value_endpoint(payload: AttributeValueCreate):
    obj = AttributeValue(**payload.model_dump())
    return {"status": "success", "data": await create_attribute_value(obj)}


# --------------------------
# LIST
# --------------------------
@router.get("/list")
async def list_attribute_values():
    return {"status": "success", "data": await get_all_attribute_values()}


# --------------------------
# GET BY ATTRIBUTE
# --------------------------
@router.get("/attribute/{attribute_id}")
async def get_by_attribute(attribute_id: str):
    return {
        "status": "success",
        "data": await get_values_by_attribute(attribute_id)
    }


# --------------------------
# GET BY ID
# --------------------------
@router.get("/{id}")
async def get_attribute_value_endpoint(id: str):
    data = await get_attribute_value_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "success", "data": data}


# --------------------------
# UPDATE
# --------------------------
@router.put("/{id}")
async def update_attribute_value_endpoint(id: str, payload: AttributeValueUpdate):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    data = await update_attribute_value(id, updates)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "data": data}


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_attribute_value_endpoint(id: str):
    result = await delete_attribute_value(id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "deleted_id": id}


# --------------------------
# ACTIVATE
# --------------------------
@router.put("/{id}/activate")
async def activate_attribute_value_endpoint(id: str):
    return {"status": "success", "data": await activate_attribute_value(id)}


# --------------------------
# DEACTIVATE
# --------------------------
@router.put("/{id}/deactivate")
async def deactivate_attribute_value_endpoint(id: str):
    return {"status": "success", "data": await deactivate_attribute_value(id)}
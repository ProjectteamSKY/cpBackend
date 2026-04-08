from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.product_attribute_domain import ProductAttribute
from app.services.product_attribute_service import *

router = APIRouter()


class ProductAttributeCreate(BaseModel):
    product_id: str
    attribute_id: str
    is_required: bool = True
    sort_order: int = 0


class ProductAttributeUpdate(BaseModel):
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_product_attribute_endpoint(payload: ProductAttributeCreate):
    obj = ProductAttribute(**payload.model_dump())
    return {"status": "success", "data": await create_product_attribute(obj)}


@router.get("/list")
async def get_all_product_attributes_endpoint():
    return {
        "status": "success",
        "data": await get_all_product_attributes()
    }
# --------------------------
# GET BY PRODUCT
# --------------------------
@router.get("/product/{product_id}")
async def get_product_attributes_endpoint(product_id: str):
    return {
        "status": "success",
        "data": await get_product_attributes(product_id)
    }


# --------------------------
# UPDATE
# --------------------------
@router.put("/{id}")
async def update_product_attribute_endpoint(id: str, payload: ProductAttributeUpdate):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    data = await update_product_attribute(id, updates)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "data": data}


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_product_attribute_endpoint(id: str):
    result = await delete_product_attribute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "deleted_id": id}


# --------------------------
# ACTIVATE
# --------------------------
@router.put("/{id}/activate")
async def activate_product_attribute_endpoint(id: str):
    return {"status": "success", "data": await activate_product_attribute(id)}


# --------------------------
# DEACTIVATE
# --------------------------
@router.put("/{id}/deactivate")
async def deactivate_product_attribute_endpoint(id: str):
    return {"status": "success", "data": await deactivate_product_attribute(id)}
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.product_variant_combinations_domain import ProductVariantCombaination
from app.services.product_variant_combinations_service import *
router = APIRouter()


class VariantCreate(BaseModel):
    product_id: str
    sku: Optional[str] = None
    is_active: bool = True


class VariantUpdate(BaseModel):
    sku: Optional[str] = None
    is_active: Optional[bool] = None


# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_variant_endpoint(payload: VariantCreate):
    obj = ProductVariantCombaination(**payload.model_dump())
    return {"status": "success", "data": await create_variant(obj)}


# --------------------------
# GET BY PRODUCT
# --------------------------
@router.get("/product/{product_id}")
async def get_variants_endpoint(product_id: str):
    return {"status": "success", "data": await get_variants(product_id)}


# --------------------------
# GET BY ID
# --------------------------
@router.get("/{id}")
async def get_variant_endpoint(id: str):
    data = await get_variant_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "success", "data": data}


# --------------------------
# UPDATE
# --------------------------
@router.put("/{id}")
async def update_variant_endpoint(id: str, payload: VariantUpdate):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    data = await update_variant(id, updates)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "data": data}


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_variant_endpoint(id: str):
    result = await delete_variant(id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "deleted_id": id}
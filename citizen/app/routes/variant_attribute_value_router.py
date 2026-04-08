from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.variant_attribute_value_domain import VariantAttributeValue
from app.services.variant_attribute_values_service import *
router = APIRouter()


class CreateModel(BaseModel):
    variant_id: str
    attribute_id: str
    attribute_value_id: str


# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_endpoint(payload: CreateModel):
    obj = VariantAttributeValue(**payload.model_dump())
    return {"status": "success", "data": await create_variant_attribute_value(obj)}


# --------------------------
# GET BY VARIANT
# --------------------------
@router.get("/variant/{variant_id}")
async def get_by_variant(variant_id: str):
    return {
        "status": "success",
        "data": await get_values_by_variant(variant_id)
    }


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_endpoint(id: str):
    result = await delete_variant_attribute_value(id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "deleted_id": id}
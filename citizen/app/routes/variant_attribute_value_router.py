from fastapi import APIRouter, HTTPException

from app.services.variant_attribute_values_service import (
    create_multiple_variant_attribute_values,
    get_values_by_variant,
    delete_variant_attribute_value,
    update_variant_attribute_values
)

router = APIRouter()


from pydantic import BaseModel
from typing import List

class CreateModel(BaseModel):
    variant_id: str
    attribute_id: str
    attribute_value_ids: List[str]

class UpdateModel(BaseModel):
    variant_id: str
    attribute_id: str
    attribute_value_ids: List[str]
# --------------------------
# CREATE MULTIPLE
# --------------------------
@router.post("/create")
async def create_endpoint(payload: CreateModel):
    data = await create_multiple_variant_attribute_values(payload)
    return {"status": "success", "data": data}


@router.get("/variant/{variant_id}")
async def get_by_variant(variant_id: str):
    data = await get_values_by_variant(variant_id)
    return {"status": "success", "data": data}


@router.put("/update")
async def update_endpoint(payload: UpdateModel):
    data = await update_variant_attribute_values(payload)
    return {"status": "success", "data": data}

@router.delete("/{id}")
async def delete_endpoint(id: str):
    result = await delete_variant_attribute_value(id)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "deleted_id": id}
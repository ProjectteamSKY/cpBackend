from fastapi import APIRouter, HTTPException

from app.services.variant_attribute_values_service import (
    create_multiple_variant_attribute_values,
    get_values_by_variant,
    delete_variant_attribute_value,
    update_variant_attribute_values,
    get_full_product_details,
    calculate_total_weight
)
from app.services.variant_price_service import get_prices_by_variant

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

@router.get("/product/{product_id}/full-details")
async def full_details(product_id: str):
    data = await get_full_product_details(product_id)
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

class WeightRequest(BaseModel):
    variant_id: str


@router.post("/total")
async def get_total_weight(payload: WeightRequest):

    price_tiers = await get_prices_by_variant(payload.variant_id)

    if not price_tiers:
        raise HTTPException(status_code=400, detail="No price tiers found")

    # ✅ take maximum max_qty
    quantity = max(item["max_qty"] for item in price_tiers)

    data = await calculate_total_weight(
        payload.variant_id,
        quantity
    )

    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    return {
        "status": "success",
        "data": data
    }
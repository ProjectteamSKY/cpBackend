from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.domain.variant_price_domain import VariantPrice
from app.services.variant_price_service import (
    create_variant_price,
    get_prices_by_variant,
    update_variant_price,
    delete_variant_price,
    calculate_price
)

router = APIRouter()


# -------------------------
# REQUEST MODELS
# -------------------------
class CreateModel(BaseModel):
    variant_id: str
    min_qty: int
    max_qty: Optional[int] = None
    price: float
    custom_qty: bool = False

    weight: float = 0.0
    length: float = 0.0
    breadth: float = 0.0
    height: float = 0.0


class PriceCalcModel(BaseModel):
    variant_id: str
    qty: int


# -------------------------
# CREATE
# -------------------------
@router.post("/create")
async def create_price(payload: CreateModel):
    try:
        obj = VariantPrice(**payload.model_dump())
        data = await create_variant_price(obj)

        return {
            "status": "success",
            "data": data
        }

    except ValueError as e:
        raise HTTPException(400, str(e))


# -------------------------
# GET
# -------------------------
@router.get("/variant/{variant_id}")
async def get_prices(variant_id: str):
    return {
        "status": "success",
        "data": await get_prices_by_variant(variant_id)
    }


# -------------------------
# UPDATE
# -------------------------
@router.put("/{id}")
async def update_price(id: str, payload: dict):
    return {
        "status": "success",
        "data": await update_variant_price(id, payload)
    }


# -------------------------
# DELETE
# -------------------------
@router.delete("/{id}")
async def delete_price(id: str):
    return {
        "status": "success",
        "data": await delete_variant_price(id)
    }


# -------------------------
# CALCULATE PRICE
# -------------------------
@router.post("/calculate")
async def calculate(payload: PriceCalcModel):

    if payload.qty < 1:
        raise HTTPException(400, "Quantity must be >= 1")

    result = await calculate_price(payload.variant_id, payload.qty)

    return {
        "status": "success",
        "data": result
    }
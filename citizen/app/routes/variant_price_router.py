from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.domain.variant_price_domain import VariantPrice
from app.services.variant_price_service import *

router = APIRouter()


class CreateModel(BaseModel):
    variant_id: str
    min_qty: int
    max_qty: Optional[int]
    price: float


@router.post("/create")
async def create_price(payload: CreateModel):
    obj = VariantPrice(**payload.model_dump())
    return {
        "status": "success",
        "data": await create_variant_price(obj)
    }


@router.get("/variant/{variant_id}")
async def get_prices(variant_id: str):
    return {
        "status": "success",
        "data": await get_prices_by_variant(variant_id)
    }


@router.delete("/{id}")
async def delete_price(id: str):
    return {
        "status": "success",
        "data": await delete_variant_price(id)
    }
# app/routes/product_variant_price_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product_variant_price_schema import (
    ProductVariantPriceCreateSchema,
    ProductVariantPriceUpdateSchema,
    ProductVariantPriceResponseSchema
)
from app.services.product_variant_price_service import *

from app.core.database import get_session

router = APIRouter()

@router.post("/", response_model=ProductVariantPriceResponseSchema)
async def create_price_route(data: ProductVariantPriceCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_price(data, session)

@router.get("/{price_id}", response_model=ProductVariantPriceResponseSchema)
async def get_price_route(price_id: str, session: AsyncSession = Depends(get_session)):
    return await get_price(price_id, session)

@router.get("/variant/{variant_id}", response_model=list[ProductVariantPriceResponseSchema])
async def get_prices_by_variant_route(variant_id: str, session: AsyncSession = Depends(get_session)):
    return await get_prices_by_variant(variant_id, session)

@router.put("/{price_id}", response_model=ProductVariantPriceResponseSchema)
async def update_price_route(price_id: str, data: ProductVariantPriceUpdateSchema, session: AsyncSession = Depends(get_session)):
    return await update_price(price_id, data, session)

@router.delete("/{price_id}")
async def delete_price_route(price_id: str, session: AsyncSession = Depends(get_session)):
    return await delete_price(price_id, session)

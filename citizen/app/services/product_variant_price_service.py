# app/services/product_variant_price_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domain.product_variant_price_domain import ProductVariantPrice
from app.repository.product_variant_price_repository import *

from app.schemas.product_variant_price_schema import (
    ProductVariantPriceCreateSchema,
    ProductVariantPriceUpdateSchema
)

# CREATE
async def create_price(data: ProductVariantPriceCreateSchema, session: AsyncSession):
    price = ProductVariantPrice(
        variant_id=data.variant_id,
        min_qty=data.min_qty,
        max_qty=data.max_qty,
        price=data.price
    )
    return await create_price_repo(price, session)


# GET ONE
async def get_price(price_id: str, session: AsyncSession):
    price = await get_price_by_id_repo(price_id, session)
    if not price:
        raise HTTPException(404, "Price not found")
    return price


# GET ALL BY VARIANT
async def get_prices_by_variant(variant_id: str, session: AsyncSession):
    return await get_all_prices_by_variant_repo(variant_id, session)


# UPDATE
async def update_price(price_id: str, data: ProductVariantPriceUpdateSchema, session: AsyncSession):
    updated = await update_price_repo(price_id, data.model_dump(exclude_unset=True), session)
    if not updated:
        raise HTTPException(404, "Price not found")
    return updated


# DELETE
async def delete_price(price_id: str, session: AsyncSession):
    success = await delete_price_repo(price_id, session)
    if not success:
        raise HTTPException(404, "Price not found")
    return {"message": "Price deleted successfully"}

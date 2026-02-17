from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.product_variant_schema import ProductVariantCreateSchema, ProductVariantResponseSchema
from app.services.product_variant_service import create_product_variant, get_product_variant

router = APIRouter()

@router.post("/", response_model=ProductVariantResponseSchema)
async def create_product_variant_route(data: ProductVariantCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_product_variant(data, session)

@router.get("/{variant_id}", response_model=ProductVariantResponseSchema)
async def get_product_variant_route(variant_id: str, session: AsyncSession = Depends(get_session)):
    variant = await get_product_variant(variant_id, session)
    if not variant:
        raise HTTPException(404, "ProductVariant not found")
    return variant

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.product_variant_service import *
from app.schemas.product_variant_schema import *

router = APIRouter(prefix="/product-variants", tags=["Product Variants"])

@router.post("/", response_model=ProductVariantResponseSchema)
async def create_route(data: ProductVariantCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_product_variant(data, session)

@router.get("/", response_model=list[ProductVariantResponseSchema])
async def get_all_route(session: AsyncSession = Depends(get_session)):
    return await get_all_product_variants(session)

@router.get("/{id}", response_model=ProductVariantResponseSchema)
async def get_route(id: str, session: AsyncSession = Depends(get_session)):
    return await get_product_variant(id, session)

@router.put("/{id}", response_model=ProductVariantResponseSchema)
async def update_route(id: str, data: ProductVariantUpdateSchema, session: AsyncSession = Depends(get_session)):
    return await update_product_variant(id, data, session)

@router.delete("/{id}")
async def delete_route(id: str, session: AsyncSession = Depends(get_session)):
    return await delete_product_variant(id, session)

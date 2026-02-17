from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.product_schema import ProductCreateSchema, ProductResponseSchema
from app.services.product_service import create_product, get_product

router = APIRouter()

@router.post("/", response_model=ProductResponseSchema)
async def create_product_route(data: ProductCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_product(data, session)

@router.get("/{product_id}", response_model=ProductResponseSchema)
async def get_product_route(product_id: str, session: AsyncSession = Depends(get_session)):
    product = await get_product(product_id, session)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

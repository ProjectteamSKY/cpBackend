from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.product_service import *
from app.schemas.product_schema import ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema

router = APIRouter(prefix="/api/product")

# CREATE
@router.post("/", response_model=ProductResponseSchema)
async def create_route(data: ProductCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_product(data, session)

# GET ALL PRODUCTS (no images)
@router.get("/", response_model=list[ProductResponseSchema])
async def get_all_route(session: AsyncSession = Depends(get_session)):
    return await get_all_products(session)

# GET ALL PRODUCTS WITH IMAGES
@router.get("/with_images", response_model=list[ProductResponseSchema], summary="Get all products with images")
async def get_all_products_with_images_route(session: AsyncSession = Depends(get_session)):
    return await get_all_products_with_images(session)

# GET ONE PRODUCT
@router.get("/{id}", response_model=ProductResponseSchema)
async def get_route(id: str, session: AsyncSession = Depends(get_session)):
    return await get_product(id, session)

# UPDATE
@router.put("/{id}", response_model=ProductResponseSchema)
async def update_route(id: str, data: ProductUpdateSchema, session: AsyncSession = Depends(get_session)):
    return await update_product(id, data, session)

# DELETE
@router.delete("/{id}")
async def delete_route(id: str, session: AsyncSession = Depends(get_session)):
    return await delete_product(id, session)

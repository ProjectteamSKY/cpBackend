from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.product_image_schema import ProductImageCreateSchema, ProductImageResponseSchema
from app.services.product_image_service import create_product_image, get_product_image

router = APIRouter(prefix="/product-images", tags=["ProductImages"])

@router.post("/", response_model=ProductImageResponseSchema)
async def create_product_image_route(data: ProductImageCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_product_image(data, session)

@router.get("/{image_id}", response_model=ProductImageResponseSchema)
async def get_product_image_route(image_id: str, session: AsyncSession = Depends(get_session)):
    image = await get_product_image(image_id, session)
    if not image:
        raise HTTPException(404, "ProductImage not found")
    return image

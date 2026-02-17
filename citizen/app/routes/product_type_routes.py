from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.product_type_schema import ProductTypeCreateSchema, ProductTypeResponseSchema
from app.services.product_type_service import create_product_type, get_product_type

router = APIRouter(prefix="/product-types", tags=["ProductTypes"])

@router.post("/", response_model=ProductTypeResponseSchema)
async def create_product_type_route(data: ProductTypeCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_product_type(data, session)

@router.get("/{pt_id}", response_model=ProductTypeResponseSchema)
async def get_product_type_route(pt_id: str, session: AsyncSession = Depends(get_session)):
    pt = await get_product_type(pt_id, session)
    if not pt:
        raise HTTPException(404, "ProductType not found")
    return pt

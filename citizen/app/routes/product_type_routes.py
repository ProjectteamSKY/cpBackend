from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.services.product_type_service import *

from app.schemas.product_type_schema import *

router = APIRouter(
)


@router.post("/", response_model=ProductTypeResponseSchema)
async def create_route(
    data: ProductTypeCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    return await create_product_type(data, session)


@router.get("/", response_model=list[ProductTypeResponseSchema])
async def get_all_route(
    session: AsyncSession = Depends(get_session)
):
    return await get_all_product_types(session)


@router.get("/{id}", response_model=ProductTypeResponseSchema)
async def get_route(
    id: str,
    session: AsyncSession = Depends(get_session)
):
    return await get_product_type(id, session)


@router.put("/{id}", response_model=ProductTypeResponseSchema)
async def update_route(
    id: str,
    data: ProductTypeUpdateSchema,
    session: AsyncSession = Depends(get_session)
):
    return await update_product_type(id, data, session)


@router.delete("/{id}")
async def delete_route(
    id: str,
    session: AsyncSession = Depends(get_session)
):
    return await delete_product_type(id, session)

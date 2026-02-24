# app/routes/custom_shape_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.custom_shape_service import (
    create_custom_shape,
    get_custom_shape,
    get_all_custom_shapes,
    update_custom_shape,
    delete_custom_shape
)
from app.schemas.custom_shape_schema import CustomShapeCreateSchema, CustomShapeUpdateSchema, CustomShapeResponseSchema

router = APIRouter()

@router.post("/", response_model=CustomShapeResponseSchema)
async def create_route(data: CustomShapeCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_custom_shape(data, session)

@router.get("/", response_model=list[CustomShapeResponseSchema])
async def get_all_route(session: AsyncSession = Depends(get_session)):
    return await get_all_custom_shapes(session)

@router.get("/{shape_id}", response_model=CustomShapeResponseSchema)
async def get_route(shape_id: str, session: AsyncSession = Depends(get_session)):
    return await get_custom_shape(shape_id, session)

@router.put("/{shape_id}", response_model=CustomShapeResponseSchema)
async def update_route(shape_id: str, data: CustomShapeUpdateSchema, session: AsyncSession = Depends(get_session)):
    return await update_custom_shape(shape_id, data, session)

@router.delete("/{shape_id}")
async def delete_route(shape_id: str, session: AsyncSession = Depends(get_session)):
    return await delete_custom_shape(shape_id, session)

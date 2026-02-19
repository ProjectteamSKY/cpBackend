# app/services/custom_shape_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import uuid

from app.domain.custom_shape_domain import CustomShape
from app.repository.custom_shape_repository import (
    create_custom_shape_repo,
    get_custom_shape_by_id_repo,
    get_all_custom_shapes_repo,
    update_custom_shape_repo,
    delete_custom_shape_repo
)
from app.schemas.custom_shape_schema import CustomShapeCreateSchema, CustomShapeUpdateSchema

# CREATE
async def create_custom_shape(data: CustomShapeCreateSchema, session: AsyncSession):
    shape = CustomShape(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description
    )
    return await create_custom_shape_repo(shape, session)

# GET ONE
async def get_custom_shape(shape_id: str, session: AsyncSession):
    shape = await get_custom_shape_by_id_repo(shape_id, session)
    if not shape:
        raise HTTPException(404, "CustomShape not found")
    return shape

# GET ALL
async def get_all_custom_shapes(session: AsyncSession):
    return await get_all_custom_shapes_repo(session)

# UPDATE
async def update_custom_shape(shape_id: str, data: CustomShapeUpdateSchema, session: AsyncSession):
    shape = await get_custom_shape_by_id_repo(shape_id, session)
    if not shape:
        raise HTTPException(404, "CustomShape not found")

    if data.name is not None:
        shape.name = data.name
    if data.description is not None:
        shape.description = data.description
    if data.is_active is not None:
        shape.is_active = data.is_active

    return await update_custom_shape_repo(shape, session)

# DELETE
async def delete_custom_shape(shape_id: str, session: AsyncSession):
    success = await delete_custom_shape_repo(shape_id, session)
    if not success:
        raise HTTPException(404, "CustomShape not found")
    return {"message": "CustomShape deleted successfully"}

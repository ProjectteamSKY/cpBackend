# app/repository/custom_shape_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.db.models.product_models import CustomShape as CustomShapeORM
from app.domain.custom_shape_domain import CustomShape

# CREATE
async def create_custom_shape_repo(shape: CustomShape, session: AsyncSession):
    orm = CustomShapeORM(
        id=shape.id,
        name=shape.name,
        description=shape.description,
        is_active=shape.is_active
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return CustomShape(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

# GET ONE
async def get_custom_shape_by_id_repo(shape_id: str, session: AsyncSession):
    result = await session.execute(
        select(CustomShapeORM).where(CustomShapeORM.id == shape_id, CustomShapeORM.is_active == True)
    )
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return CustomShape(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

# GET ALL
async def get_all_custom_shapes_repo(session: AsyncSession):
    result = await session.execute(
        select(CustomShapeORM)
        .where(CustomShapeORM.is_active == True)
        .order_by(CustomShapeORM.created_at.desc())
    )
    return [
        CustomShape(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
        for orm in result.scalars().all()
    ]

# UPDATE
async def update_custom_shape_repo(shape: CustomShape, session: AsyncSession):
    stmt = (
        update(CustomShapeORM)
        .where(CustomShapeORM.id == shape.id, CustomShapeORM.is_active == True)
        .values(
            name=shape.name,
            description=shape.description,
            is_active=shape.is_active,
            updated_at=datetime.utcnow()
        )
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()
    return shape

# SOFT DELETE
async def delete_custom_shape_repo(shape_id: str, session: AsyncSession):
    stmt = (
        update(CustomShapeORM)
        .where(CustomShapeORM.id == shape_id, CustomShapeORM.is_active == True)
        .values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
        .execution_options(synchronize_session="fetch")
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0

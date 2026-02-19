import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.product_models import CutType as CutTypeORM
from app.domain.cut_type_domain import CutType


# CREATE
async def create_cut_type_repo(
    session: AsyncSession,
    cut_type: CutType
):

    orm = CutTypeORM(
        id=cut_type.id,
        name=cut_type.name,
        description=cut_type.description,
        is_active=True
    )

    session.add(orm)

    await session.commit()

    await session.refresh(orm)

    return orm


# GET ALL
async def get_all_cut_types_repo(
    session: AsyncSession
):

    result = await session.execute(
        select(CutTypeORM)
        .order_by(CutTypeORM.created_at.desc())
    )

    return result.scalars().all()


# GET BY ID
async def get_cut_type_by_id_repo(
    session: AsyncSession,
    cut_type_id: str
):

    result = await session.execute(
        select(CutTypeORM)
        .where(
            CutTypeORM.id == cut_type_id,
            CutTypeORM.is_active == True
        )
    )

    return result.scalar_one_or_none()


# UPDATE
async def update_cut_type_repo(
    session: AsyncSession,
    cut_type_id: str,
    data: dict
):

    await session.execute(
        update(CutTypeORM)
        .where(CutTypeORM.id == cut_type_id)
        .values(**data)
    )

    await session.commit()

    return await get_cut_type_by_id_repo(session, cut_type_id)


# SOFT DELETE
async def delete_cut_type_repo(
    session: AsyncSession,
    cut_type_id: str
):

    await session.execute(
        update(CutTypeORM)
        .where(CutTypeORM.id == cut_type_id)
        .values(is_active=False)
    )

    await session.commit()

    return True

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.models.product_models import PaperType as PaperTypeORM
from app.domain.paper_type_domain import PaperType


# CREATE
async def create_paper_type_repo(
    pt: PaperType,
    session: AsyncSession
) -> PaperType:

    orm = PaperTypeORM(
        id=pt.id,
        name=pt.name,
        description=pt.description,
        is_active=True
    )

    session.add(orm)

    await session.commit()
    await session.refresh(orm)

    return map_to_domain(orm)


# GET BY ID
async def get_paper_type_by_id_repo(
    pt_id: str,
    session: AsyncSession
) -> PaperType | None:

    result = await session.execute(
        select(PaperTypeORM)
        .where(
            PaperTypeORM.id == pt_id,
            PaperTypeORM.is_active == True
        )
    )

    orm = result.scalar_one_or_none()

    if not orm:
        return None

    return map_to_domain(orm)


# GET ALL
async def get_all_paper_types_repo(
    session: AsyncSession
) -> list[PaperType]:

    result = await session.execute(
        select(PaperTypeORM)
        .order_by(PaperTypeORM.created_at.desc())
    )

    return [map_to_domain(orm) for orm in result.scalars().all()]


# UPDATE
async def update_paper_type_repo(
    pt_id: str,
    data: dict,
    session: AsyncSession
) -> PaperType | None:

    stmt = (
        update(PaperTypeORM)
        .where(
            PaperTypeORM.id == pt_id,
            PaperTypeORM.is_active == True
        )
        .values(
            **data,
            updated_at=datetime.utcnow()
        )
        .execution_options(synchronize_session="fetch")
    )

    result = await session.execute(stmt)

    if result.rowcount == 0:
        return None

    await session.commit()

    return await get_paper_type_by_id_repo(pt_id, session)


# SOFT DELETE
async def delete_paper_type_repo(
    pt_id: str,
    session: AsyncSession
) -> bool:

    stmt = (
        update(PaperTypeORM)
        .where(
            PaperTypeORM.id == pt_id,
            PaperTypeORM.is_active == True
        )
        .values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
    )

    result = await session.execute(stmt)

    await session.commit()

    return result.rowcount > 0


# MAPPER
def map_to_domain(orm: PaperTypeORM) -> PaperType:

    return PaperType(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

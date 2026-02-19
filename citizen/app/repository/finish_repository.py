from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.models.product_models import Finish as FinishORM

from app.domain.finish_domain import Finish


# CREATE
async def create_finish_repo(
    finish: Finish,
    session: AsyncSession
) -> Finish:

    orm = FinishORM(
        id=finish.id,
        name=finish.name,
        description=finish.description,
        is_active=True
    )

    session.add(orm)

    await session.commit()

    await session.refresh(orm)

    return map_to_domain(orm)


# GET BY ID
async def get_finish_by_id_repo(
    finish_id: str,
    session: AsyncSession
) -> Finish | None:

    result = await session.execute(
        select(FinishORM)
        .where(
            FinishORM.id == finish_id,
            FinishORM.is_active == True
        )
    )

    orm = result.scalar_one_or_none()

    if not orm:
        return None

    return map_to_domain(orm)


# GET ALL
async def get_all_finishes_repo(
    session: AsyncSession
) -> list[Finish]:

    result = await session.execute(
        select(FinishORM)
        .order_by(FinishORM.created_at.desc())
    )

    return [
        map_to_domain(orm)
        for orm in result.scalars().all()
    ]


# UPDATE
async def update_finish_repo(
    finish_id: str,
    data: dict,
    session: AsyncSession
) -> Finish | None:

    stmt = (
        update(FinishORM)
        .where(
            FinishORM.id == finish_id,
            FinishORM.is_active == True
        )
        .values(
            **data,
            updated_at=datetime.utcnow()
        )
        .execution_options(
            synchronize_session="fetch"
        )
    )

    result = await session.execute(stmt)

    if result.rowcount == 0:
        return None

    await session.commit()

    return await get_finish_by_id_repo(finish_id, session)


# SOFT DELETE
async def delete_finish_repo(
    finish_id: str,
    session: AsyncSession
) -> bool:

    stmt = (
        update(FinishORM)
        .where(
            FinishORM.id == finish_id,
            FinishORM.is_active == True
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
def map_to_domain(orm: FinishORM) -> Finish:

    return Finish(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

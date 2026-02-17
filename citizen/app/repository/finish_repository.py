from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Finish as FinishORM
from app.domain.finish_domain import Finish as FinishDomain

async def create_finish_repo(finish: FinishDomain, session: AsyncSession):
    orm = FinishORM(id=finish.id, name=finish.name, description=finish.description)
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return FinishDomain(id=orm.id, name=orm.name, description=orm.description)

async def get_finish_by_id_repo(finish_id: str, session: AsyncSession):
    result = await session.execute(select(FinishORM).where(FinishORM.id == finish_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return FinishDomain(id=orm.id, name=orm.name, description=orm.description)

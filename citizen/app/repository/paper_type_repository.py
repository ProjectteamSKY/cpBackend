from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import PaperType as PaperTypeORM
from app.domain.paper_type_domain import PaperType as PaperTypeDomain

async def create_paper_type_repo(pt: PaperTypeDomain, session: AsyncSession):
    orm = PaperTypeORM(id=pt.id, name=pt.name, description=pt.description)
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return PaperTypeDomain(id=orm.id, name=orm.name, description=orm.description)

async def get_paper_type_by_id_repo(pt_id: str, session: AsyncSession):
    result = await session.execute(select(PaperTypeORM).where(PaperTypeORM.id == pt_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return PaperTypeDomain(id=orm.id, name=orm.name, description=orm.description)

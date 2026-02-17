from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import CutType as CutTypeORM
from app.domain.cut_type_domain import CutType as CutTypeDomain

async def create_cut_type_repo(cut_type: CutTypeDomain, session: AsyncSession):
    orm = CutTypeORM(id=cut_type.id, name=cut_type.name, description=cut_type.description)
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return CutTypeDomain(id=orm.id, name=orm.name, description=orm.description)

async def get_cut_type_by_id_repo(cut_type_id: str, session: AsyncSession):
    result = await session.execute(select(CutTypeORM).where(CutTypeORM.id == cut_type_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return CutTypeDomain(id=orm.id, name=orm.name, description=orm.description)

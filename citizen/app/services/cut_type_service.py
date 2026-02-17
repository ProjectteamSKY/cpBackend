from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.cut_type_repository import create_cut_type_repo, get_cut_type_by_id_repo
from app.domain.cut_type_domain import CutType as CutTypeDomain

async def create_cut_type(data, session: AsyncSession):
    cut_type = CutTypeDomain(name=data.name, description=data.description)
    return await create_cut_type_repo(cut_type, session)

async def get_cut_type(cut_type_id: str, session: AsyncSession):
    return await get_cut_type_by_id_repo(cut_type_id, session)

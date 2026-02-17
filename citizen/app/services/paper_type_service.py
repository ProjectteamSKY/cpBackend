from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.paper_type_repository import create_paper_type_repo, get_paper_type_by_id_repo
from app.domain.paper_type import PaperType as PaperTypeDomain

async def create_paper_type(data, session: AsyncSession):
    pt = PaperTypeDomain(name=data.name, description=data.description)
    return await create_paper_type_repo(pt, session)

async def get_paper_type(pt_id: str, session: AsyncSession):
    return await get_paper_type_by_id_repo(pt_id, session)

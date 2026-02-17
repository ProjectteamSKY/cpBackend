from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.finish_repository import create_finish_repo, get_finish_by_id_repo
from app.domain.finish_domain import Finish as FinishDomain

async def create_finish(data, session: AsyncSession):
    finish = FinishDomain(name=data.name, description=data.description)
    return await create_finish_repo(finish, session)

async def get_finish(finish_id: str, session: AsyncSession):
    return await get_finish_by_id_repo(finish_id, session)

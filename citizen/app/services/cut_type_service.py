from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.cut_type_domain import CutType
from app.repository.cut_type_repository import *


async def create_cut_type_service(
    session: AsyncSession,
    name: str,
    description: str | None
):

    cut_type = CutType(
        name=name,
        description=description
    )

    return await create_cut_type_repo(session, cut_type)


async def get_all_cut_types_service(
    session: AsyncSession
):
    return await get_all_cut_types_repo(session)


async def get_cut_type_service(
    session: AsyncSession,
    cut_type_id: str
):
    return await get_cut_type_by_id_repo(session, cut_type_id)


async def update_cut_type_service(
    session: AsyncSession,
    cut_type_id: str,
    data: dict
):
    return await update_cut_type_repo(session, cut_type_id, data)


async def delete_cut_type_service(
    session: AsyncSession,
    cut_type_id: str
):
    return await delete_cut_type_repo(session, cut_type_id)

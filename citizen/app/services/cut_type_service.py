from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.cut_type_domain import CutType
from app.utils.query_loader import load_queries

queries = load_queries()


async def create_cut_type(cut_type: CutType, session: AsyncSession):

    await session.execute(
        text(queries["cut_type"]["create"]),
        cut_type.to_dict()
    )

    await session.commit()

    return await get_cut_type_by_id(cut_type.id, session)


async def get_all_cut_types(session: AsyncSession):

    result = await session.execute(
        text(queries["cut_type"]["get_all"])
    )

    return [dict(row._mapping) for row in result.fetchall()]


async def get_cut_type_by_id(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["cut_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


async def update_cut_type(id: str, name: str, description: str, session: AsyncSession):

    await session.execute(
        text(queries["cut_type"]["update"]),
        {
            "id": id,
            "name": name,
            "description": description,
            "updated_at": CutType(name=name).updated_at
        }
    )

    await session.commit()

    return await get_cut_type_by_id(id, session)


async def delete_cut_type(id: str, session: AsyncSession):

    await session.execute(
        text(queries["cut_type"]["soft_delete"]),
        {"id": id}
    )

    await session.commit()

    return {"message": "Cut Type deleted successfully"}


async def activate_cut_type(id: str, session: AsyncSession):

    await session.execute(
        text(queries["cut_type"]["activate"]),
        {"id": id}
    )

    await session.commit()

    return await get_cut_type_by_id(id, session)
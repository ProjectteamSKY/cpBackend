from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.size_domain import Size
from app.utils.query_loader import load_queries

queries = load_queries()


async def create_size(size: Size, session: AsyncSession):

    await session.execute(
        text(queries["size"]["create"]),
        size.to_dict()
    )

    await session.commit()

    return await get_size_by_id(size.id, session)


async def get_all_sizes(session: AsyncSession):

    result = await session.execute(
        text(queries["size"]["get_all"])
    )

    return [dict(row._mapping) for row in result.fetchall()]


async def get_size_by_id(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["size"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


async def update_size(
    id: str,
    name: str,
    width: float,
    height: float,
    unit: str,
    description: str,
    session: AsyncSession
):

    await session.execute(
        text(queries["size"]["update"]),
        {
            "id": id,
            "name": name,
            "width": width,
            "height": height,
            "unit": unit,
            "description": description,
            "updated_at": Size(
                name=name,
                width=width,
                height=height,
                unit=unit
            ).updated_at
        }
    )

    await session.commit()

    return await get_size_by_id(id, session)


async def delete_size(id: str, session: AsyncSession):

    await session.execute(
        text(queries["size"]["soft_delete"]),
        {"id": id}
    )

    await session.commit()

    return {"message": "Size deleted successfully"}


async def activate_size(id: str, session: AsyncSession):

    await session.execute(
        text(queries["size"]["activate"]),
        {"id": id}
    )

    await session.commit()

    return await get_size_by_id(id, session)

async def deactivate_size(id: str, session: AsyncSession):

    await session.execute(
        text(queries["size"]["deactivate"]),
        {"id": id}
    )

    await session.commit()

    return await get_size_by_id(id, session)
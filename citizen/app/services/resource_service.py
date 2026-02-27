from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.resource_domain import Resource
from app.utils.query_loader import load_queries

queries = load_queries()


async def create_resource(resource: Resource, session: AsyncSession):
    await session.execute(
        text(queries["resource"]["create_resource"]),
        {
            "id": resource.id,
            "name": resource.name,
            "description": resource.description,
        },
    )
    await session.commit()

    return {
        "id": resource.id,
        "name": resource.name,
        "description": resource.description,
    }


async def get_resource_by_name(name: str, session: AsyncSession):
    result = await session.execute(
        text(queries["resource"]["get_by_name"]),
        {"name": name},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_resource_by_id(resource_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["resource"]["get_by_id"]),
        {"resource_id": resource_id},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_all_resources(session: AsyncSession):
    result = await session.execute(text(queries["resource"]["get_all"]))
    return [dict(r._mapping) for r in result.fetchall()]


async def delete_resource(resource_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["resource"]["delete_resource"]),
        {"resource_id": resource_id},
    )
    await session.commit()
    return result.rowcount > 0
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.role_domain import Role
from app.utils.query_loader import load_queries

queries = load_queries()


async def create_role(role: Role, session: AsyncSession):
    await session.execute(
        text(queries["role"]["create_role"]),
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
        },
    )
    await session.commit()

    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
    }


async def get_role_by_name(name: str, session: AsyncSession):
    result = await session.execute(
        text(queries["role"]["get_by_name"]),
        {"name": name},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_role_by_id(role_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["role"]["get_by_id"]),
        {"role_id": role_id},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_all_roles(session: AsyncSession):
    result = await session.execute(text(queries["role"]["get_all"]))
    return [dict(r._mapping) for r in result.fetchall()]


async def delete_role(role_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["role"]["delete_role"]),
        {"role_id": role_id},
    )
    await session.commit()
    return result.rowcount > 0
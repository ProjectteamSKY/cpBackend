from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.permission_domain import Permission
from app.utils.query_loader import load_queries

queries = load_queries()


async def create_permission(permission: Permission, session: AsyncSession):
    await session.execute(
        text(queries["permission"]["create_permission"]),
        {
            "id": permission.id,
            "resource_id": permission.resource_id,
            "action": permission.action,
            "method": permission.method,
            "path": permission.path,
            "description": permission.description,
        },
    )
    await session.commit()

    return {
        "id": permission.id,
        "resource_id": permission.resource_id,
        "action": permission.action,
        "method": permission.method,
        "path": permission.path,
        "description": permission.description,
    }


async def get_permission_by_id(permission_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["permission"]["get_by_id"]),
        {"permission_id": permission_id},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_all_permissions(session: AsyncSession):
    result = await session.execute(text(queries["permission"]["get_all"]))
    return [dict(r._mapping) for r in result.fetchall()]


async def get_permissions_by_resource(resource_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["permission"]["get_by_resource"]),
        {"resource_id": resource_id},
    )
    return [dict(r._mapping) for r in result.fetchall()]


async def delete_permission(permission_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["permission"]["delete_permission"]),
        {"permission_id": permission_id},
    )
    await session.commit()
    return result.rowcount > 0
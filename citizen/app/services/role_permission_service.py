from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.role_permission_domain import RolePermission
from app.utils.query_loader import load_queries

queries = load_queries()


async def assign_permission(role_permission: RolePermission, session: AsyncSession):
    await session.execute(
        text(queries["role_permission"]["assign_permission"]),
        {
            "id": role_permission.id,
            "role_id": role_permission.role_id,
            "permission_id": role_permission.permission_id,
        },
    )
    await session.commit()

    return {
        "id": role_permission.id,
        "role_id": role_permission.role_id,
        "permission_id": role_permission.permission_id,
    }


async def get_permissions_by_role(role_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["role_permission"]["get_permissions_by_role"]),
        {"role_id": role_id},
    )
    return [dict(row._mapping) for row in result.fetchall()]


async def get_roles_by_permission(permission_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["role_permission"]["get_roles_by_permission"]),
        {"permission_id": permission_id},
    )
    return [dict(row._mapping) for row in result.fetchall()]


async def remove_permission(role_id: str, permission_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["role_permission"]["remove_permission"]),
        {
            "role_id": role_id,
            "permission_id": permission_id,
        },
    )
    await session.commit()
    return result.rowcount > 0
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.user_role_domain import UserRole
from app.utils.query_loader import load_queries

queries = load_queries()


async def assign_role(user_role: UserRole, session: AsyncSession):
    await session.execute(
        text(queries["user_role"]["assign_role"]),
        {
            "id": user_role.id,
            "user_id": user_role.user_id,
            "role_id": user_role.role_id,
            "assigned_by": user_role.assigned_by,
        },
    )
    await session.commit()

    return {
        "id": user_role.id,
        "user_id": user_role.user_id,
        "role_id": user_role.role_id,
        "assigned_by": user_role.assigned_by,
    }


async def get_roles_by_user(user_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user_role"]["get_roles_by_user"]),
        {"user_id": user_id},
    )
    return [dict(row._mapping) for row in result.fetchall()]


async def get_users_by_role(role_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user_role"]["get_users_by_role"]),
        {"role_id": role_id},
    )
    return [dict(row._mapping) for row in result.fetchall()]


async def remove_role(user_id: str, role_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user_role"]["remove_role"]),
        {
            "user_id": user_id,
            "role_id": role_id,
        },
    )
    await session.commit()
    return result.rowcount > 0
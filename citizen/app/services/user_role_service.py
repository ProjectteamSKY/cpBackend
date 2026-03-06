from app.domain.user_role_domain import UserRole
from app.utils.query_loader import load_queries
from app.core.database import execute, query_all

queries = load_queries()


async def assign_role(user_role: UserRole):
    await execute(
        queries["user_role"]["assign_role"],
        {
            "id": user_role.id,
            "user_id": user_role.user_id,
            "role_id": user_role.role_id,
            "assigned_by": user_role.assigned_by,
        },
    )

    return {
        "id": user_role.id,
        "user_id": user_role.user_id,
        "role_id": user_role.role_id,
        "assigned_by": user_role.assigned_by,
    }


async def get_roles_by_user(user_id: str):
    return await query_all(
        queries["user_role"]["get_roles_by_user"],
        {"user_id": user_id},
    )


async def get_users_by_role(role_id: str):
    return await query_all(
        queries["user_role"]["get_users_by_role"],
        {"role_id": role_id},
    )


async def remove_role(user_id: str, role_id: str):
    result = await execute(
        queries["user_role"]["remove_role"],
        {
            "user_id": user_id,
            "role_id": role_id,
        },
    )

    return result > 0
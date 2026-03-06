from app.domain.role_permission_domain import RolePermission
from app.utils.query_loader import load_queries
from app.core.database import execute, query_all

queries = load_queries()


async def assign_permission(role_permission: RolePermission):
    await execute(
        queries["role_permission"]["assign_permission"],
        {
            "id": role_permission.id,
            "role_id": role_permission.role_id,
            "permission_id": role_permission.permission_id,
        },
    )

    return {
        "id": role_permission.id,
        "role_id": role_permission.role_id,
        "permission_id": role_permission.permission_id,
    }


async def get_permissions_by_role(role_id: str):
    return await query_all(
        queries["role_permission"]["get_permissions_by_role"],
        {"role_id": role_id},
    )


async def get_roles_by_permission(permission_id: str):
    return await query_all(
        queries["role_permission"]["get_roles_by_permission"],
        {"permission_id": permission_id},
    )


async def remove_permission(role_id: str, permission_id: str):
    result = await execute(
        queries["role_permission"]["remove_permission"],
        {
            "role_id": role_id,
            "permission_id": permission_id,
        },
    )

    return result > 0
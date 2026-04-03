from app.domain.role_permission_domain import RolePermission
from app.utils.query_loader import load_queries
from app.core.database import query, execute

queries = load_queries()


async def assign_role_permission_service(rp: RolePermission):
    return await execute(
        queries["role_permission"]["assign_role_permission"],
        [rp.role_id, rp.permission_id],
        fetch_row=True,
    )


async def get_permissions_by_role_service(role_id: int):
    return await query(
        queries["role_permission"]["get_permissions_by_role"],
        [role_id],
        fetch_all=True,
    )


async def remove_role_permission_service(role_id: int, permission_id: int):
    row = await execute(
        queries["role_permission"]["remove_role_permission"],
        [role_id, permission_id],
        fetch_row=True,
    )
    return bool(row)


async def get_all_role_permissions_service():
    return await query(
        queries["role_permission"]["get_all_role_permissions"],
        fetch_all=True,
    )
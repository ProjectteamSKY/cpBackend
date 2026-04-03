from app.domain.permission_domain import Permission
from app.utils.query_loader import load_queries
from app.core.database import query, execute

queries = load_queries()


async def create_permission(p: Permission):
    return await execute(
        queries["permission"]["create_permission"],
        [p.resource_id, p.action, p.method, p.path, p.description],
        fetch_row=True,
    )


async def get_all_permissions():
    return await query(queries["permission"]["get_all_permissions"], fetch_all=True)


async def delete_permission(permission_id: int):
    return await execute(
        queries["permission"]["delete_permission"],
        [permission_id],
        fetch_row=True,
    )
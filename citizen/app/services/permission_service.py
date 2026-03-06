from app.domain.permission_domain import Permission
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


async def create_permission(permission: Permission):
    await execute(
        queries["permission"]["create_permission"],
        {
            "id": permission.id,
            "resource_id": permission.resource_id,
            "action": permission.action,
            "method": permission.method,
            "path": permission.path,
            "description": permission.description,
        },
    )

    return {
        "id": permission.id,
        "resource_id": permission.resource_id,
        "action": permission.action,
        "method": permission.method,
        "path": permission.path,
        "description": permission.description,
    }


async def get_permission_by_id(permission_id: str):
    return await query(
        queries["permission"]["get_by_id"],
        {"permission_id": permission_id},
    )


async def get_all_permissions():
    return await query_all(
        queries["permission"]["get_all"]
    )


async def get_permissions_by_resource(resource_id: str):
    return await query_all(
        queries["permission"]["get_by_resource"],
        {"resource_id": resource_id},
    )


async def delete_permission(permission_id: str):
    result = await execute(
        queries["permission"]["delete_permission"],
        {"permission_id": permission_id},
    )

    return result > 0
from app.domain.role_domain import Role
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


async def create_role(role: Role):
    await execute(
        queries["role"]["create_role"],
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
        },
    )

    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
    }


async def get_role_by_name(name: str):
    return await query(
        queries["role"]["get_by_name"],
        {"name": name},
    )


async def get_role_by_id(role_id: str):
    return await query(
        queries["role"]["get_by_id"],
        {"role_id": role_id},
    )


async def get_all_roles():
    return await query_all(
        queries["role"]["get_all"]
    )


async def delete_role(role_id: str):
    result = await execute(
        queries["role"]["delete_role"],
        {"role_id": role_id},
    )

    return result > 0
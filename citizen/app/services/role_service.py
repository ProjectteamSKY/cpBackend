from app.domain.role_domain import Role
from app.utils.query_loader import load_queries
from app.core.database import query, execute

queries = load_queries()


async def create_role(r: Role):
    return await execute(
        queries["role"]["create_role"],
        [r.name, r.description],
        fetch_row=True,
    )


async def get_all_roles():
    return await query(queries["role"]["get_all_roles"], fetch_all=True)


async def delete_role(role_id: int):
    row = await execute(
        queries["role"]["delete_role"],
        [role_id],
        fetch_row=True,
    )
    return bool(row)
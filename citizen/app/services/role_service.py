from fastapi import HTTPException
from app.domain.role_domain import Role
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# ------------------------- #
# CREATE
# ------------------------- #
async def create_role(role: Role):
    existing = await query(
        "SELECT * FROM roles WHERE name = :name AND is_deleted = FALSE",
        {"name": role.name},
    )
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")

    await execute(queries["role"]["create"], role.to_dict())
    created = await query(queries["role"]["get_by_id"], {"id": role.id})
    return created

# ------------------------- #
# GET ALL
# ------------------------- #
async def get_all_roles():
    return await query_all(queries["role"]["get_all"])

# ------------------------- #
# GET BY ID
# ------------------------- #
async def get_role_by_id(id: str):
    return await query(queries["role"]["get_by_id"], {"id": id})

# ------------------------- #
# UPDATE
# ------------------------- #
async def update_role(id: str, updates: dict):
    if not updates:
        return await get_role_by_id(id)
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["role"]["update"].format(set_clause=set_clause)
    await execute(sql, {"id": id, **updates})
    return await get_role_by_id(id)

# ------------------------- #
# DELETE (soft)
# ------------------------- #
async def delete_role(id: str):
    existing = await query(queries["role"]["get_by_id"], {"id": id})
    if not existing:
        return None
    await execute(queries["role"]["delete"], {"id": id})
    return {"id": id}

# ------------------------- #
# ACTIVATE
# ------------------------- #
async def activate_role(id: str):
    await execute(queries["role"]["activate"], {"id": id})
    return await get_role_by_id(id)

# ------------------------- #
# DEACTIVATE
# ------------------------- #
async def deactivate_role(id: str):
    await execute(queries["role"]["deactivate"], {"id": id})
    return await get_role_by_id(id)
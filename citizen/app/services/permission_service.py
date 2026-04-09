from fastapi import HTTPException
from app.domain.permission_domain import Permission
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# ------------------------- #
# CREATE
# ------------------------- #
async def create_permission(permission: Permission):
    existing = await query(
        "SELECT * FROM permissions WHERE action = :action AND path = :path AND is_deleted = FALSE",
        {"action": permission.action, "path": permission.path},
    )
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")

    await execute(queries["permission"]["create"], permission.to_dict())
    created = await query(queries["permission"]["get_by_id"], {"id": permission.id})
    return created

# ------------------------- #
# GET ALL
# ------------------------- #
async def get_all_permissions():
    return await query_all(queries["permission"]["get_all"])

# ------------------------- #
# GET BY ID
# ------------------------- #
async def get_permission_by_id(id: str):
    return await query(queries["permission"]["get_by_id"], {"id": id})

# ------------------------- #
# UPDATE
# ------------------------- #
async def update_permission(id: str, updates: dict):
    if not updates:
        return await get_permission_by_id(id)
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["permission"]["update"].format(set_clause=set_clause)
    await execute(sql, {"id": id, **updates})
    return await get_permission_by_id(id)

# ------------------------- #
# DELETE (soft)
# ------------------------- #
async def delete_permission(id: str):
    existing = await query(queries["permission"]["get_by_id"], {"id": id})
    if not existing:
        return None
    await execute(queries["permission"]["delete"], {"id": id})
    return {"id": id}

# ------------------------- #
# ACTIVATE
# ------------------------- #
async def activate_permission(id: str):
    await execute(queries["permission"]["activate"], {"id": id})
    return await get_permission_by_id(id)

# ------------------------- #
# DEACTIVATE
# ------------------------- #
async def deactivate_permission(id: str):
    await execute(queries["permission"]["deactivate"], {"id": id})
    return await get_permission_by_id(id)
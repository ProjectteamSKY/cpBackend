from fastapi import HTTPException
from app.domain.role_permission_domain import RolePermission
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# ------------------------- #
# CREATE / ASSIGN PERMISSION
# ------------------------- #
async def create_role_permission(rp: RolePermission):
    existing = await query(
        "SELECT * FROM role_permissions WHERE role_id = :role_id AND permission_id = :permission_id",
        {"role_id": rp.role_id, "permission_id": rp.permission_id},
    )
    if existing:
        raise HTTPException(status_code=400, detail="Permission already assigned to this role")

    await execute(queries["role_permission"]["create"], rp.to_dict())
    created = await query(queries["role_permission"]["get_by_id"], {"id": rp.id})
    return created

# ------------------------- #
# GET ALL
# ------------------------- #
async def get_all_role_permissions():
    return await query_all(queries["role_permission"]["get_all"])

# ------------------------- #
# GET BY ID
# ------------------------- #
async def get_role_permission_by_id(id: str):
    return await query(queries["role_permission"]["get_by_id"], {"id": id})

# ------------------------- #
# GET BY ROLE ID
# ------------------------- #
async def get_role_permissions_by_role(role_id: str):
    return await query_all(queries["role_permission"]["get_by_role_id"], {"role_id": role_id})

# ------------------------- #
# GET BY PERMISSION ID
# ------------------------- #
async def get_role_permissions_by_permission(permission_id: str):
    return await query_all(queries["role_permission"]["get_by_permission_id"], {"permission_id": permission_id})

# ------------------------- #
# UPDATE
# ------------------------- #
async def update_role_permission(id: str, updates: dict):
    if not updates:
        return await get_role_permission_by_id(id)
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["role_permission"]["update"].format(set_clause=set_clause)
    await execute(sql, {"id": id, **updates})
    return await get_role_permission_by_id(id)

# ------------------------- #
# DELETE
# ------------------------- #
async def delete_role_permission(id: str):
    existing = await query(queries["role_permission"]["get_by_id"], {"id": id})
    if not existing:
        return None
    await execute(queries["role_permission"]["delete"], {"id": id})
    return {"id": id}
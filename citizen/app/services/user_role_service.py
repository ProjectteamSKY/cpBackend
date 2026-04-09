from fastapi import HTTPException
from app.domain.user_role_domain import UserRole
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# ------------------------- #
# CREATE / ASSIGN ROLE
# ------------------------- #
async def create_user_role(user_role: UserRole):
    existing = await query(
        "SELECT * FROM user_roles WHERE user_id = :user_id AND role_id = :role_id",
        {"user_id": user_role.user_id, "role_id": user_role.role_id},
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already has this role assigned")

    await execute(queries["user_role"]["create"], user_role.to_dict())
    created = await query(queries["user_role"]["get_by_id"], {"id": user_role.id})
    return created

# ------------------------- #
# GET ALL USER ROLES
# ------------------------- #
async def get_all_user_roles():
    return await query_all(queries["user_role"]["get_all"])

# ------------------------- #
# GET BY ID
# ------------------------- #
async def get_user_role_by_id(id: str):
    return await query(queries["user_role"]["get_by_id"], {"id": id})

# ------------------------- #
# GET BY USER ID
# ------------------------- #
async def get_user_roles_by_user(user_id: str):
    return await query_all(queries["user_role"]["get_by_user_id"], {"user_id": user_id})

# ------------------------- #
# UPDATE
# ------------------------- #
async def update_user_role(id: str, updates: dict):
    if not updates:
        return await get_user_role_by_id(id)
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["user_role"]["update"].format(set_clause=set_clause)
    await execute(sql, {"id": id, **updates})
    return await get_user_role_by_id(id)

# ------------------------- #
# DELETE
# ------------------------- #
async def delete_user_role(id: str):
    existing = await query(queries["user_role"]["get_by_id"], {"id": id})
    if not existing:
        return None
    await execute(queries["user_role"]["delete"], {"id": id})
    return {"id": id}
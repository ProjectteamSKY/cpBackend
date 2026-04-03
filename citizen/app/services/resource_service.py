from fastapi import HTTPException
from app.domain.resource_domain import Resource
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# ------------------------- #
# CREATE
# ------------------------- #
async def create_resource(resource: Resource):
    existing = await query(
        "SELECT * FROM resources WHERE name = :name AND is_deleted = FALSE",
        {"name": resource.name},
    )
    if existing:
        raise HTTPException(status_code=400, detail="Resource name already exists")

    await execute(queries["resource"]["create"], resource.to_dict())
    created = await query(queries["resource"]["get_by_id"], {"id": resource.id})
    return created

# ------------------------- #
# GET ALL
# ------------------------- #
async def get_all_resources():
    return await query_all(queries["resource"]["get_all"])

# ------------------------- #
# GET BY ID
# ------------------------- #
async def get_resource_by_id(id: str):
    return await query(queries["resource"]["get_by_id"], {"id": id})

# ------------------------- #
# UPDATE
# ------------------------- #
async def update_resource(id: str, updates: dict):
    if not updates:
        return await get_resource_by_id(id)
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["resource"]["update"].format(set_clause=set_clause)
    await execute(sql, {"id": id, **updates})
    return await get_resource_by_id(id)

# ------------------------- #
# DELETE (soft)
# ------------------------- #
async def delete_resource(id: str):
    existing = await query(queries["resource"]["get_by_id"], {"id": id})
    if not existing:
        return None
    await execute(queries["resource"]["delete"], {"id": id})
    return {"id": id}

# ------------------------- #
# ACTIVATE
# ------------------------- #
async def activate_resource(id: str):
    await execute(queries["resource"]["activate"], {"id": id})
    return await get_resource_by_id(id)

# ------------------------- #
# DEACTIVATE
# ------------------------- #
async def deactivate_resource(id: str):
    await execute(queries["resource"]["deactivate"], {"id": id})
    return await get_resource_by_id(id)
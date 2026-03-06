# app/services/size_service.py

from fastapi import HTTPException
from app.domain.size_domain import Size
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_size(size: Size):
    """
    Create a new size.
    If size with same name exists → raise error.
    Returns the created size as dict.
    """
    existing = await query(
        "SELECT * FROM sizes WHERE name = :name AND is_deleted = FALSE",
        {"name": size.name}
    )

    if existing:
        raise HTTPException(status_code=400, detail="Size name already exists")

    await execute(queries["size"]["create"], size.to_dict())
    created = await query(queries["size"]["get_by_id"], {"id": size.id})
    return created


# -------------------------
# GET ALL
# -------------------------
async def get_all_sizes():
    """
    Fetch all sizes as a list of dicts
    """
    return await query_all(queries["size"]["get_all"])


# -------------------------
# GET ALL ACTIVE
# -------------------------
async def get_all_sizes_active():
    """
    Fetch all active sizes
    """
    return await query_all(queries["size"]["get_all_active"])


# -------------------------
# GET BY ID
# -------------------------
async def get_size_by_id(id: str):
    """
    Fetch a single size by ID
    """
    return await query(queries["size"]["get_by_id"], {"id": id})


# -------------------------
# UPDATE
# -------------------------
async def update_size(id: str, updates: dict):
    """
    Update size fields by ID
    """
    if not updates:
        return await get_size_by_id(id)

    # Add updated_at timestamp
    updates["updated_at"] = Size(
        name=updates.get("name"),
        width=updates.get("width"),
        height=updates.get("height"),
        unit=updates.get("unit")
    ).updated_at

    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["size"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_size_by_id(id)


# -------------------------
# DELETE (soft delete)
# -------------------------
async def delete_size(id: str):
    """
    Soft-delete a size by ID
    """
    existing = await query(queries["size"]["get_by_id"], {"id": id})
    if not existing:
        return None

    await execute(queries["size"]["soft_delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_size(id: str):
    """
    Activate a soft-deleted size
    """
    await execute(queries["size"]["activate"], {"id": id})
    return await get_size_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_size(id: str):
    """
    Deactivate a size
    """
    await execute(queries["size"]["deactivate"], {"id": id})
    return await get_size_by_id(id)
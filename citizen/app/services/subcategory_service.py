# app/services/subcategory_service.py

from fastapi import HTTPException
from app.domain.subcategory_domain import Subcategory
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_subcategory(subcategory: Subcategory):
    """
    Create a new subcategory.
    If subcategory exists and is active → raise error.
    If subcategory exists but soft-deleted → reactivate it.
    Returns the created or reactivated subcategory as dict.
    """
    existing = await query(
        "SELECT * FROM subcategories WHERE name = :name AND category_id = :category_id AND is_deleted = FALSE",
        {"name": subcategory.name, "category_id": subcategory.category_id}
    )

    if existing:
        raise HTTPException(status_code=400, detail="Subcategory already exists")

    await execute(queries["subcategory"]["create"], subcategory.to_dict())
    created = await query(queries["subcategory"]["get_by_id"], {"id": subcategory.id})
    return created


# -------------------------
# GET ALL
# -------------------------
async def get_all_subcategories():
    """
    Fetch all subcategories as a list of dicts
    """
    return await query_all(queries["subcategory"]["get_all"])


# -------------------------
# GET BY ID
# -------------------------
async def get_subcategory_by_id(id: str):
    """
    Fetch a single subcategory by ID
    """
    return await query(queries["subcategory"]["get_by_id"], {"id": id})


# -------------------------
# GET BY CATEGORY
# -------------------------
async def get_subcategories_by_category(category_id: str):
    """
    Fetch all subcategories for a specific category
    """
    return await query_all(queries["subcategory"]["get_by_category"], {"category_id": category_id})


# -------------------------
# UPDATE
# -------------------------
async def update_subcategory(id: str, updates: dict):
    """
    Update subcategory fields by ID
    """
    if not updates:
        return await get_subcategory_by_id(id)

    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["subcategory"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_subcategory_by_id(id)


# -------------------------
# DELETE (soft delete)
# -------------------------
async def delete_subcategory(id: str):
    """
    Soft-delete a subcategory by ID
    """
    existing = await query(queries["subcategory"]["get_by_id"], {"id": id})
    if not existing:
        return None

    await execute(queries["subcategory"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_subcategory(id: str):
    """
    Activate a soft-deleted subcategory
    """
    await execute(queries["subcategory"]["activate"], {"id": id})
    return await get_subcategory_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_subcategory(id: str):
    """
    Deactivate a subcategory
    """
    await execute(queries["subcategory"]["deactivate"], {"id": id})
    return await get_subcategory_by_id(id)
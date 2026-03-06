# app/services/cut_type_service.py

from fastapi import HTTPException
from app.domain.cut_type_domain import CutType
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_cut_type(cut_type: CutType):
    """
    Create a new cut type.
    If already exists and not deleted → raise error.
    """

    existing = await query(
        "SELECT * FROM cut_types WHERE name = :name AND is_deleted = FALSE",
        {"name": cut_type.name}
    )

    if existing:
        raise HTTPException(status_code=400, detail="Cut type already exists")

    await execute(
        queries["cut_type"]["create"],
        cut_type.to_dict()
    )

    return await get_cut_type_by_id(cut_type.id)


# -------------------------
# GET ALL
# -------------------------
async def get_all_cut_types():
    """
    Fetch all cut types
    """
    return await query_all(
        queries["cut_type"]["get_all"]
    )


# -------------------------
# GET ALL ACTIVE
# -------------------------
async def get_all_cut_types_active():
    """
    Fetch all active cut types
    """
    return await query_all(
        queries["cut_type"]["get_all_active"]
    )


# -------------------------
# GET BY ID
# -------------------------
async def get_cut_type_by_id(id: str):
    """
    Fetch single cut type by ID
    """
    return await query(
        queries["cut_type"]["get_by_id"],
        {"id": id}
    )


# -------------------------
# UPDATE (Dynamic)
# -------------------------
async def update_cut_type(id: str, updates: dict):
    """
    Update cut type fields dynamically
    """

    if not updates:
        return await get_cut_type_by_id(id)

    # Add updated_at timestamp
    updates["updated_at"] = CutType(
        name=updates.get("name")
    ).updated_at

    set_clause = ", ".join(
        f"{key} = :{key}" for key in updates.keys()
    )

    sql = queries["cut_type"]["update"].format(
        set_clause=set_clause
    )

    await execute(sql, {"id": id, **updates})

    return await get_cut_type_by_id(id)


# -------------------------
# SOFT DELETE
# -------------------------
async def delete_cut_type(id: str):
    """
    Soft delete cut type
    """

    existing = await query(
        queries["cut_type"]["get_by_id"],
        {"id": id}
    )

    if not existing:
        return None

    await execute(
        queries["cut_type"]["soft_delete"],
        {"id": id}
    )

    return {"id": id, "deleted": True}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_cut_type(id: str):
    """
    Activate cut type
    """

    await execute(
        queries["cut_type"]["activate"],
        {"id": id}
    )

    return await get_cut_type_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_cut_type(id: str):
    """
    Deactivate cut type
    """

    cut_type = await get_cut_type_by_id(id)

    if not cut_type or not cut_type.get("is_active", True):
        return None

    await execute(
        queries["cut_type"]["deactivate"],
        {"id": id}
    )

    return await get_cut_type_by_id(id)
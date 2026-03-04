# app/services/print_type_service.py

from fastapi import HTTPException
from app.domain.print_type_domain import PrintType
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_print_type(print_type: PrintType):
    """
    Create a new print type.
    If name already exists and not deleted → raise error.
    """

    existing = await query(
        "SELECT * FROM print_types WHERE name = :name AND is_deleted = FALSE",
        {"name": print_type.name}
    )

    if existing:
        raise HTTPException(status_code=400, detail="Print type already exists")

    await execute(queries["print_type"]["create"], print_type.to_dict())

    created = await query(
        queries["print_type"]["get_by_id"],
        {"id": print_type.id}
    )

    return created


# -------------------------
# GET ALL
# -------------------------
async def get_all_print_types():
    """
    Fetch all print types
    """
    return await query_all(queries["print_type"]["get_all"])


# -------------------------
# GET ALL ACTIVE
# -------------------------
async def get_all_print_types_active():
    """
    Fetch all active print types
    """
    return await query_all(queries["print_type"]["get_all_active"])


# -------------------------
# GET BY ID
# -------------------------
async def get_print_type_by_id(id: str):
    """
    Fetch single print type by ID
    """
    return await query(
        queries["print_type"]["get_by_id"],
        {"id": id}
    )


# -------------------------
# UPDATE
# -------------------------
async def update_print_type(id: str, updates: dict):
    """
    Update print type fields dynamically
    """

    if not updates:
        return await get_print_type_by_id(id)

    # Optional: Add updated_at if your table supports it
    updates["updated_at"] = PrintType(
        name=updates.get("name")
    ).updated_at

    set_clause = ", ".join(
        f"{key} = :{key}" for key in updates.keys()
    )

    sql = queries["print_type"]["update"].format(
        set_clause=set_clause
    )

    await execute(sql, {"id": id, **updates})

    return await get_print_type_by_id(id)


# -------------------------
# SOFT DELETE
# -------------------------
async def delete_print_type(id: str):
    """
    Soft delete print type
    """

    existing = await query(
        queries["print_type"]["get_by_id"],
        {"id": id}
    )

    if not existing:
        return None

    await execute(
        queries["print_type"]["delete"],
        {"id": id}
    )

    return {"id": id, "deleted": True}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_print_type(id: str):
    """
    Activate print type
    """

    await execute(
        queries["print_type"]["activate"],
        {"id": id}
    )

    return await get_print_type_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_print_type(id: str):
    """
    Deactivate print type
    """

    await execute(
        queries["print_type"]["deactivate"],
        {"id": id}
    )

    return await get_print_type_by_id(id)
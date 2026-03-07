from fastapi import HTTPException
from app.domain.paper_type_domain import PaperType
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# -------------------------
# CREATE
# -------------------------
async def create_paper_type(paper_type: PaperType):
    existing = await query(
        "SELECT * FROM paper_types WHERE name = :name AND is_deleted = FALSE",
        {"name": paper_type.name}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Paper type already exists")

    await execute(
        queries["paper_type"]["create"],
        paper_type.to_dict()
    )

    return await query(
        queries["paper_type"]["get_by_id"],
        {"id": paper_type.id}
    )

# -------------------------
# GET ALL
# -------------------------
async def get_all_paper_types():
    return await query_all(queries["paper_type"]["get_all"])

async def get_all_paper_types_active():
    return await query_all(queries["paper_type"]["get_all_active"])

# -------------------------
# GET BY ID
# -------------------------
async def get_paper_type_by_id(id: str):
    return await query(queries["paper_type"]["get_by_id"], {"id": id})

# -------------------------
# UPDATE
# -------------------------
async def update_paper_type(id: str, updates: dict):
    existing = await get_paper_type_by_id(id)
    if not existing:
        return None

    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["paper_type"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_paper_type_by_id(id)

# -------------------------
# DELETE (SOFT)
# -------------------------
async def delete_paper_type(id: str):
    existing = await get_paper_type_by_id(id)
    if not existing:
        return None

    await execute(queries["paper_type"]["delete"], {"id": id})
    return {"id": id}

# -------------------------
# ACTIVATE / DEACTIVATE
# -------------------------
async def activate_paper_type(id: str):
    existing = await get_paper_type_by_id(id)
    if not existing:
        return None
    await execute(queries["paper_type"]["activate"], {"id": id})
    return await get_paper_type_by_id(id)

async def deactivate_paper_type(id: str):
    existing = await get_paper_type_by_id(id)
    if not existing:
        return None
    await execute(queries["paper_type"]["deactivate"], {"id": id})
    return await get_paper_type_by_id(id)
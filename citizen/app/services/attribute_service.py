from fastapi import HTTPException
from app.domain.attributes_domain import Attribute
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


async def create_attribute(attribute: Attribute):
    existing = await query(
        "SELECT * FROM attributes WHERE name = :name AND is_deleted = FALSE",
        {"name": attribute.name}
    )

    if existing:
        raise HTTPException(status_code=400, detail="Attribute already exists")

    await execute(queries["attributes"]["create"], attribute.to_dict())
    return await query(queries["attributes"]["get_by_id"], {"id": attribute.id})


async def get_all_attributes():
    return await query_all(queries["attributes"]["get_all"])


async def get_attribute_by_id(id: str):
    return await query(queries["attributes"]["get_by_id"], {"id": id})


async def update_attribute(id: str, updates: dict):
    if not updates:
        return await get_attribute_by_id(id)

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    sql = queries["attributes"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_attribute_by_id(id)


async def delete_attribute(id: str):
    existing = await get_attribute_by_id(id)
    if not existing:
        return None

    await execute(queries["attributes"]["delete"], {"id": id})
    return {"id": id}


async def activate_attribute(id: str):
    await execute(queries["attributes"]["activate"], {"id": id})
    return await get_attribute_by_id(id)


async def deactivate_attribute(id: str):
    await execute(queries["attributes"]["deactivate"], {"id": id})
    return await get_attribute_by_id(id)
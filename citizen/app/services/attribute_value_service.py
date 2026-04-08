from fastapi import HTTPException
from app.domain.attribute_value_domain import AttributeValue
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_attribute_value(attr_val: AttributeValue):

    existing = await query(
        """
        SELECT * FROM attribute_values
        WHERE attribute_id = :attribute_id
        AND value = :value
        AND is_deleted = FALSE
        """,
        {
            "attribute_id": attr_val.attribute_id,
            "value": attr_val.value
        }
    )

    if existing:
        raise HTTPException(status_code=400, detail="Value already exists for this attribute")

    await execute(queries["attribute_values"]["create"], attr_val.to_dict())
    return await query(queries["attribute_values"]["get_by_id"], {"id": attr_val.id})


# -------------------------
# GET ALL
# -------------------------
async def get_all_attribute_values():
    return await query_all(queries["attribute_values"]["get_all"])


# -------------------------
# GET BY ID
# -------------------------
async def get_attribute_value_by_id(id: str):
    return await query(queries["attribute_values"]["get_by_id"], {"id": id})


# -------------------------
# GET BY ATTRIBUTE
# -------------------------
async def get_values_by_attribute(attribute_id: str):
    return await query_all(
        queries["attribute_values"]["get_by_attribute"],
        {"attribute_id": attribute_id}
    )


# -------------------------
# UPDATE
# -------------------------
async def update_attribute_value(id: str, updates: dict):
    if not updates:
        return await get_attribute_value_by_id(id)

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    sql = queries["attribute_values"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_attribute_value_by_id(id)


# -------------------------
# DELETE
# -------------------------
async def delete_attribute_value(id: str):
    existing = await get_attribute_value_by_id(id)
    if not existing:
        return None

    await execute(queries["attribute_values"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_attribute_value(id: str):
    await execute(queries["attribute_values"]["activate"], {"id": id})
    return await get_attribute_value_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_attribute_value(id: str):
    await execute(queries["attribute_values"]["deactivate"], {"id": id})
    return await get_attribute_value_by_id(id)
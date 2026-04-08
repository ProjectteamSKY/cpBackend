from fastapi import HTTPException
from app.domain.variant_attribute_value_domain import VariantAttributeValue
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_variant_attribute_value(obj: VariantAttributeValue):

    # ✅ Check duplicate
    existing = await query(
        """
        SELECT * FROM variant_attribute_values
        WHERE variant_id = :variant_id
        AND attribute_id = :attribute_id
        AND is_deleted = FALSE
        """,
        {
            "variant_id": obj.variant_id,
            "attribute_id": obj.attribute_id
        }
    )

    if existing:
        raise HTTPException(status_code=400, detail="Attribute already assigned to variant")

    # ✅ Validate attribute_value belongs to attribute
    value = await query(
        """
        SELECT * FROM attribute_values
        WHERE id = :id AND is_deleted = FALSE
        """,
        {"id": obj.attribute_value_id}
    )

    if not value:
        raise HTTPException(status_code=400, detail="Invalid attribute value")

    if value["attribute_id"] != obj.attribute_id:
        raise HTTPException(
            status_code=400,
            detail="Attribute value does not belong to given attribute"
        )

    await execute(queries["variant_attribute_values"]["create"], obj.to_dict())
    return await query(
        queries["variant_attribute_values"]["get_by_id"],
        {"id": obj.id}
    )


# -------------------------
# GET BY VARIANT
# -------------------------
async def get_values_by_variant(variant_id: str):
    return await query_all(
        queries["variant_attribute_values"]["get_by_variant"],
        {"variant_id": variant_id}
    )


# -------------------------
# UPDATE
# -------------------------
async def update_variant_attribute_value(id: str, updates: dict):

    if not updates:
        return await query(
            queries["variant_attribute_values"]["get_by_id"],
            {"id": id}
        )

    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    sql = queries["variant_attribute_values"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await query(
        queries["variant_attribute_values"]["get_by_id"],
        {"id": id}
    )


# -------------------------
# DELETE
# -------------------------
async def delete_variant_attribute_value(id: str):
    existing = await query(
        queries["variant_attribute_values"]["get_by_id"],
        {"id": id}
    )
    if not existing:
        return None

    await execute(queries["variant_attribute_values"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_variant_attribute_value(id: str):
    await execute(queries["variant_attribute_values"]["activate"], {"id": id})
    return await query(
        queries["variant_attribute_values"]["get_by_id"],
        {"id": id}
    )


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_variant_attribute_value(id: str):
    await execute(queries["variant_attribute_values"]["deactivate"], {"id": id})
    return await query(
        queries["variant_attribute_values"]["get_by_id"],
        {"id": id}
    )
from fastapi import HTTPException
from app.domain.variant_price_domain import VariantPrice
from app.utils.variant_price_validator import (
    validate_basic,
    validate_no_overlap
)
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_variant_price(obj: VariantPrice):

    # ✅ Validate
    validate_basic(obj.min_qty, obj.max_qty, obj.price)

    if obj.weight < 0:
        raise HTTPException(400, "Weight cannot be negative")

    # Fetch existing slabs
    rows = await query_all(
        """
        SELECT min_qty, max_qty
        FROM variant_prices
        WHERE variant_id = :variant_id
        AND is_deleted = FALSE
        """,
        {"variant_id": obj.variant_id}
    )

    await validate_no_overlap(rows, obj.min_qty, obj.max_qty)

    # Insert
    await execute(
        queries["variant_prices"]["create"],
        obj.to_dict()
    )

    return await query(
        queries["variant_prices"]["get_by_id"],
        {"id": obj.id}
    )


# -------------------------
# GET
# -------------------------
async def get_prices_by_variant(variant_id: str):
    return await query_all(
        queries["variant_prices"]["get_by_variant"],
        {"variant_id": variant_id}
    )


# -------------------------
# UPDATE
# -------------------------
async def update_variant_price(id: str, updates: dict):

    existing = await query(
        queries["variant_prices"]["get_by_id"],
        {"id": id}
    )

    if not existing:
        raise HTTPException(404, "Price not found")

    if not updates:
        raise HTTPException(400, "No fields to update")

    new_min = updates.get("min_qty", existing["min_qty"])
    new_max = updates.get("max_qty", existing["max_qty"])
    new_price = updates.get("price", existing["price"])
    new_weight = updates.get("weight", existing.get("weight", 0))

    validate_basic(new_min, new_max, new_price)

    if new_weight < 0:
        raise HTTPException(400, "Weight cannot be negative")

    rows = await query_all(
        """
        SELECT min_qty, max_qty
        FROM variant_prices
        WHERE variant_id = :variant_id
        AND id != :id
        AND is_deleted = FALSE
        """,
        {
            "variant_id": existing["variant_id"],
            "id": id
        }
    )

    await validate_no_overlap(rows, new_min, new_max)

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    sql = queries["variant_prices"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})

    return await query(
        queries["variant_prices"]["get_by_id"],
        {"id": id}
    )


# -------------------------
# DELETE (SOFT)
# -------------------------
async def delete_variant_price(id: str):
    await execute(
        queries["variant_prices"]["delete"],
        {"id": id}
    )
    return {"id": id}
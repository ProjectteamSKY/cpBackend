from fastapi import HTTPException

from app.domain.variant_price_domain import VariantPrice
from app.utils.variant_price_validator import validate_basic, validate_no_overlap
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_variant_price(obj: VariantPrice):

    validate_basic(obj.min_qty, obj.max_qty, obj.price)

    rows = await query_all(
        """
        SELECT min_qty, max_qty, custom_qty
        FROM variant_prices
        WHERE variant_id = :variant_id
        AND is_deleted = FALSE
        """,
        {"variant_id": obj.variant_id}
    )

    # ✅ ONLY FOR SLAB
    if not obj.custom_qty:
        await validate_no_overlap(rows, obj.min_qty, obj.max_qty)

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
    new_custom = updates.get("custom_qty", existing["custom_qty"])

    validate_basic(new_min, new_max, new_price)

    rows = await query_all(
        """
        SELECT min_qty, max_qty, custom_qty
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

    if not new_custom:
        await validate_no_overlap(rows, new_min, new_max)

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    sql = queries["variant_prices"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})

    return await query(
        queries["variant_prices"]["get_by_id"],
        {"id": id}
    )


# -------------------------
# DELETE
# -------------------------
async def delete_variant_price(id: str):
    await execute(
        queries["variant_prices"]["delete"],
        {"id": id}
    )
    return {"id": id}

async def get_variant_price_by_id(variant_price_id: str):
    """
    Fetch a single variant price by ID with full validation.
    """

    row = await query(
        """
        SELECT *
        FROM variant_prices
        WHERE id = :id
        AND is_deleted = FALSE
        """,
        {"id": variant_price_id}
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Variant price not found: {variant_price_id}"
        )

    if not row.get("is_active"):
        raise HTTPException(
            status_code=400,
            detail="Variant price is inactive"
        )

    return row
# -------------------------
# CALCULATE PRICE
# -------------------------
async def calculate_price(variant_id: str, qty: int):

    rows = await query_all(
        """
        SELECT *
        FROM variant_prices
        WHERE variant_id = :variant_id
        AND is_deleted = FALSE
        AND is_active = TRUE
        ORDER BY min_qty ASC
        """,
        {"variant_id": variant_id}
    )

    if not rows:
        raise HTTPException(404, "No pricing configured")

    for row in rows:

        # ✅ CUSTOM
        if row["custom_qty"]:
            return {
                "type": "custom",
                "unit_price": float(row["price"]),
                "quantity": qty,
                "total_price": qty * float(row["price"])
            }

        # ✅ SLAB
        if row["max_qty"] is not None:
            if row["min_qty"] <= qty <= row["max_qty"]:
                return {
                    "type": "slab",
                    "quantity": qty,
                    "total_price": float(row["price"])
                }

    raise HTTPException(400, "No matching price slab found")
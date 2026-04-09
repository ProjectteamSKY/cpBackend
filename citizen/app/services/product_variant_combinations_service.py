from fastapi import HTTPException
from app.domain.product_variant_combinations_domain import ProductVariantCombaination
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_variant(obj: ProductVariantCombaination):

    await execute(queries["product_variant_combinations"]["create"], obj.to_dict())
    return await query(queries["product_variant_combinations"]["get_by_id"], {"id": obj.id})


# -------------------------
# GET BY PRODUCT
# -------------------------
async def get_variants(product_id: str):
    return await query_all(
        queries["product_variant_combinations"]["get_by_product"],
        {"product_id": product_id}
    )


# -------------------------
# GET BY ID
# -------------------------
async def get_variant_by_id(id: str):
    return await query(queries["product_variant_combinations"]["get_by_id"], {"id": id})


# -------------------------
# UPDATE
# -------------------------
async def update_variant(id: str, updates: dict):
    if not updates:
        return await get_variant_by_id(id)

    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    sql = queries["product_variant_combinations"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_variant_by_id(id)


# -------------------------
# DELETE
# -------------------------
async def delete_variant(id: str):
    existing = await get_variant_by_id(id)
    if not existing:
        return None

    await execute(queries["product_variant_combinations"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_variant(id: str):
    await execute(queries["product_variant_combinations"]["activate"], {"id": id})
    return await get_variant_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_variant(id: str):
    await execute(queries["product_variant_combinations"]["deactivate"], {"id": id})
    return await get_variant_by_id(id)
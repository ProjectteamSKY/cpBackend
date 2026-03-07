from datetime import datetime
from app.domain.product_variant_price_domain import ProductVariantPrice
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# ---------------- CREATE ----------------
async def create_product_variant_price(pvp: ProductVariantPrice):
    sql = queries["product_variant_price"]["create"]  # ❌ no text()
    await execute(sql, pvp.to_dict())
    return pvp.to_dict()


# ---------------- GET ALL ----------------
async def get_all_product_variant_prices():
    sql = queries["product_variant_price"]["get_all"]
    rows = await query_all(sql)
    return [dict(r) for r in rows]


# ---------------- GET BY ID ----------------
async def get_product_variant_price_by_id(id: str):
    sql = queries["product_variant_price"]["get_by_id"]
    row = await query(sql, {"id": id})
    return dict(row) if row else None


# ---------------- GET BY VARIANT ----------------
async def get_product_variant_prices_by_variant(variant_id: str):
    sql = queries["product_variant_price"]["get_by_variant"]
    rows = await query_all(sql, {"variant_id": variant_id})
    return [dict(r) for r in rows]


# ---------------- UPDATE ----------------
async def update_product_variant_price(id: str, updates: dict):

    existing = await get_product_variant_price_by_id(id)
    if not existing:
        return None

    final_data = {
        "id": id,
        "variant_id": updates.get("variant_id", existing["variant_id"]),
        "discount_id": updates.get("discount_id", existing["discount_id"]),
        "min_qty": updates.get("min_qty", existing["min_qty"]),
        "price": updates.get("price", existing["price"]),
        "updated_at": datetime.utcnow(),
        "is_active": updates.get("is_active", existing.get("is_active")),
    }

    sql = queries["product_variant_price"]["update"]

    await execute(sql, final_data)

    return await get_product_variant_price_by_id(id)


# ---------------- SOFT DELETE ----------------
async def soft_delete_product_variant_price(id: str):
    sql = queries["product_variant_price"]["soft_delete"]
    await execute(sql, {"id": id})
    return {"status": "success", "deleted_id": id}


# ---------------- ACTIVATE ----------------
async def activate_product_variant_price(id: str):
    sql = queries["product_variant_price"]["activate"]
    await execute(sql, {"id": id})
    return {"status": "success", "activated_id": id}


# ---------------- DEACTIVATE ----------------
async def deactivate_product_variant_price(id: str):
    sql = queries["product_variant_price"]["deactivate"]
    await execute(sql, {"id": id})
    return {"status": "success", "deactivated_id": id}


async def get_variant_with_paper_and_size(variant_id: str):
    sql = """
    SELECT
        pv.id,
        s.width,
        s.height,
        pt.gsm
    FROM product_variants pv
    LEFT JOIN sizes s ON pv.size_id = s.id
    LEFT JOIN paper_types pt ON pv.paper_type_id = pt.id
    WHERE pv.id = :variant_id
    """
    row = await query(sql, {"variant_id": variant_id})
    return dict(row) if row else None
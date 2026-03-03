from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.domain.product_variant_price_domain import ProductVariantPrice
from app.utils.query_loader import load_queries

queries = load_queries()

# ---------------- CREATE ----------------
async def create_product_variant_price(pvp: ProductVariantPrice, session: AsyncSession):
    sql = text(queries["product_variant_price"]["create"])
    await session.execute(sql, pvp.to_dict())
    await session.commit()
    return pvp.to_dict()

# ---------------- GET ALL ----------------
async def get_all_product_variant_prices(session: AsyncSession):
    sql = text(queries["product_variant_price"]["get_all"])
    result = await session.execute(sql)
    return [dict(r._mapping) for r in result.fetchall()]

# ---------------- GET BY ID ----------------
async def get_product_variant_price_by_id(id: str, session: AsyncSession):
    sql = text(queries["product_variant_price"]["get_by_id"])
    result = await session.execute(sql, {"id": id})
    row = result.fetchone()
    return dict(row._mapping) if row else None

# ---------------- GET BY VARIANT ----------------
async def get_product_variant_prices_by_variant(variant_id: str, session: AsyncSession):
    sql = text(queries["product_variant_price"]["get_by_variant"])
    result = await session.execute(sql, {"variant_id": variant_id})
    return [dict(r._mapping) for r in result.fetchall()]

# ---------------- UPDATE ----------------
async def update_product_variant_price(id: str, updates: dict, session: AsyncSession):

    # 1️⃣ Get existing record first
    existing = await get_product_variant_price_by_id(id, session)

    if not existing:
        return None

    # 2️⃣ Merge existing values with updates
    final_data = {
        "id": id,
        "variant_id": updates.get("variant_id", existing["variant_id"]),
        "discount_id": updates.get("discount_id", existing["discount_id"]),
        "min_qty": updates.get("min_qty", existing["min_qty"]),
        "price": updates.get("price", existing["price"]),
        "updated_at": datetime.utcnow(),
    }

    # Optional: if you want to update is_active too
    if "is_active" in updates:
        final_data["is_active"] = updates["is_active"]

    sql = text(queries["product_variant_price"]["update"])

    await session.execute(sql, final_data)
    await session.commit()

    return await get_product_variant_price_by_id(id, session)

# ---------------- SOFT DELETE ----------------
async def soft_delete_product_variant_price(id: str, session: AsyncSession):
    sql = text(queries["product_variant_price"]["soft_delete"])
    await session.execute(sql, {"id": id})
    await session.commit()
    return {"status": "success", "deleted_id": id}

# ---------------- ACTIVATE ----------------
async def activate_product_variant_price(id: str, session: AsyncSession):
    sql = text(queries["product_variant_price"]["activate"])
    await session.execute(sql, {"id": id})
    await session.commit()
    return {"status": "success", "activated_id": id}

async def deactivate_product_variant_price(id: str, session: AsyncSession):
    sql = text(queries["product_variant_price"]["deactivate"])
    await session.execute(sql, {"id": id})
    await session.commit()
    return {"status": "success", "deactivated_id": id}
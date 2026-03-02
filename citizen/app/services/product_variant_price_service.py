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
    updates["updated_at"] = datetime.utcnow()
    sql = text(queries["product_variant_price"]["update"])
    params = {"id": id, **updates}
    await session.execute(sql, params)
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
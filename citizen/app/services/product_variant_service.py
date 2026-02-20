from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.product_variant_domain import ProductVariant
from app.utils.query_loader import load_queries

queries = load_queries()


async def create_product_variant(variant: ProductVariant, session: AsyncSession):
    await session.execute(text(queries["product_variant"]["create"]), variant.to_dict())
    await session.commit()
    return await get_product_variant_by_id(variant.id, session)


async def get_all_product_variants(session: AsyncSession):
    result = await session.execute(text(queries["product_variant"]["get_all"]))
    return [dict(r._mapping) for r in result.fetchall()]


async def get_product_variant_by_id(id: str, session: AsyncSession):
    result = await session.execute(text(queries["product_variant"]["get_by_id"]), {"id": id})
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_product_variants_by_product(product_id: str, session: AsyncSession):
    result = await session.execute(text(queries["product_variant"]["get_by_product"]), {"product_id": product_id})
    return [dict(r._mapping) for r in result.fetchall()]


async def update_product_variant(id: str, variant: ProductVariant, session: AsyncSession):
    await session.execute(text(queries["product_variant"]["update"]), {**variant.to_dict(), "id": id})
    await session.commit()
    return await get_product_variant_by_id(id, session)


async def delete_product_variant(id: str, session: AsyncSession):
    await session.execute(text(queries["product_variant"]["soft_delete"]), {"id": id})
    await session.commit()
    return {"message": "Product Variant deleted successfully"}


async def activate_product_variant(id: str, session: AsyncSession):
    await session.execute(text(queries["product_variant"]["activate"]), {"id": id})
    await session.commit()
    return await get_product_variant_by_id(id, session)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.domain.product_discount_domain import ProductDiscount
from app.utils.query_loader import load_queries

queries = load_queries()

async def create_product_discount(discount: ProductDiscount, session: AsyncSession):
    await session.execute(text(queries["product_discount"]["create"]), discount.to_dict())
    await session.commit()
    return await get_product_discount_by_id(discount.id, session)

async def get_all_product_discounts(session: AsyncSession):
    result = await session.execute(text(queries["product_discount"]["get_all"]))
    return [dict(r._mapping) for r in result.fetchall()]

async def get_all_product_discounts_active(session: AsyncSession):
    result = await session.execute(text(queries["product_discount"]["get_all_active"]))
    return [dict(r._mapping) for r in result.fetchall()]


async def get_product_discount_by_id(id: str, session: AsyncSession):
    result = await session.execute(text(queries["product_discount"]["get_by_id"]), {"id": id})
    row = result.fetchone()
    return dict(row._mapping) if row else None

async def get_product_discounts_by_product(product_id: str, session: AsyncSession):
    result = await session.execute(text(queries["product_discount"]["get_by_product"]), {"product_id": product_id})
    return [dict(r._mapping) for r in result.fetchall()]

async def update_product_discount(id: str, discount: ProductDiscount, session: AsyncSession):
    await session.execute(text(queries["product_discount"]["update"]), {**discount.to_dict(), "id": id})
    await session.commit()
    return await get_product_discount_by_id(id, session)

async def delete_product_discount(id: str, session: AsyncSession):
    await session.execute(text(queries["product_discount"]["soft_delete"]), {"id": id})
    await session.commit()
    return {"message": "Product Discount deleted successfully"}

async def activate_product_discount(id: str, session: AsyncSession):
    await session.execute(text(queries["product_discount"]["activate"]), {"id": id})
    await session.commit()
    return await get_product_discount_by_id(id, session)

async def deactivate_product_discount(id: str, session: AsyncSession):
    await session.execute(text(queries["product_discount"]["deactivate"]), {"id": id})
    await session.commit()
    return await get_product_discount_by_id(id, session)


async def get_product_discounts_by_date_range(start_date: datetime, end_date: datetime, session: AsyncSession):
    result = await session.execute(
        text(queries["product_discount"]["get_by_date_range"]),
        {"start_date": start_date, "end_date": end_date}
    )
    return [dict(r._mapping) for r in result.fetchall()]
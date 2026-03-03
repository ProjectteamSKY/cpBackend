from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.product_domain import Product
from app.utils.query_loader import load_queries
import json

queries = load_queries()


async def create_product(product: Product, session: AsyncSession):
    await session.execute(
        text(queries["product"]["create"]),
        {
            **product.to_dict(),
            "images": json.dumps(product.images),
            "related_images": json.dumps(product.related_images),
        }
    )
    await session.commit()
    return await get_product_by_id(product.id, session)


async def get_all_products(session: AsyncSession):
    result = await session.execute(text(queries["product"]["get_all"]))
    products = [dict(r._mapping) for r in result.fetchall()]

    # Parse the JSON string columns
    for p in products:
        if "images" in p and isinstance(p["images"], str):
            p["images"] = json.loads(p["images"])
        if "related_images" in p and isinstance(p["related_images"], str):
            p["related_images"] = json.loads(p["related_images"])

    return products
async def get_all_products_active(session: AsyncSession):
    result = await session.execute(text(queries["product"]["get_all_active"]))
    products = [dict(r._mapping) for r in result.fetchall()]

    # Parse the JSON string columns
    for p in products:
        if "images" in p and isinstance(p["images"], str):
            p["images"] = json.loads(p["images"])
        if "related_images" in p and isinstance(p["related_images"], str):
            p["related_images"] = json.loads(p["related_images"])

    return products



async def get_product_by_id(id: str, session: AsyncSession):
    result = await session.execute(text(queries["product"]["get_by_id"]), {"id": id})
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_products_by_category(category_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["product"]["get_by_category"]), {"category_id": category_id}
    )
    return [dict(r._mapping) for r in result.fetchall()]


async def update_product(product_id: str, product: Product, session: AsyncSession):
    await session.execute(
        text(queries["product"]["update"]),
        {
            "id": product_id,
            "category_id": product.category_id,
            "subcategory_id": product.subcategory_id,
            "name": product.name,
            "description": product.description,
            "min_order_qty": product.min_order_qty,
            "max_order_qty": product.max_order_qty,
            "images": json.dumps(product.images),
            "related_images": json.dumps(product.related_images),
            "updated_at": product.updated_at,
        }
    )
    await session.commit()
    return await get_product_by_id(product_id, session)


async def delete_product(product_id: str, session: AsyncSession):
    await session.execute(text(queries["product"]["delete"]), {"id": product_id})
    await session.commit()
    return {"message": "Product deleted successfully"}


async def activate_product(product_id: str, session: AsyncSession):
    await session.execute(text(queries["product"]["activate"]), {"id": product_id})
    await session.commit()
    return await get_product_by_id(product_id, session)

async def deactivate_product(product_id: str, session: AsyncSession):
    await session.execute(text(queries["product"]["deactivate"]), {"id": product_id})
    await session.commit()
    return await get_product_by_id(product_id, session)
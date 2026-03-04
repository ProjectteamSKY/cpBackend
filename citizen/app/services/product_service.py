import json
from app.domain.product_domain import Product
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# ===================================
# CREATE
# ===================================
async def create_product(product: Product):
    await execute(
        queries["product"]["create"],
        {
            **product.to_dict(),
            "images": json.dumps(product.images),
            "related_images": json.dumps(product.related_images),
        }
    )
    return await get_product_by_id(product.id)


# ===================================
# GET ALL
# ===================================
async def get_all_products():
    products = await query_all(queries["product"]["get_all"])

    for p in products:
        if p.get("images"):
            p["images"] = json.loads(p["images"])
        if p.get("related_images"):
            p["related_images"] = json.loads(p["related_images"])

    return products


async def get_all_products_active():
    products = await query_all(queries["product"]["get_all_active"])

    for p in products:
        if p.get("images"):
            p["images"] = json.loads(p["images"])
        if p.get("related_images"):
            p["related_images"] = json.loads(p["related_images"])

    return products


# ===================================
# GET BY ID
# ===================================
async def get_product_by_id(product_id: str):
    product = await query(
        queries["product"]["get_by_id"],
        {"id": product_id}
    )

    if product and product.get("images"):
        product["images"] = json.loads(product["images"])

    if product and product.get("related_images"):
        product["related_images"] = json.loads(product["related_images"])

    return product


# ===================================
# GET BY CATEGORY
# ===================================
async def get_products_by_category(category_id: str):
    products = await query_all(
        queries["product"]["get_by_category"],
        {"category_id": category_id}
    )

    return products


# ===================================
# UPDATE
# ===================================
async def update_product(product_id: str, product: Product):
    await execute(
        queries["product"]["update"],
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

    return await get_product_by_id(product_id)


# ===================================
# DELETE
# ===================================
async def delete_product(product_id: str):
    await execute(
        queries["product"]["delete"],
        {"id": product_id}
    )
    return {"message": "Product deleted successfully"}


# ===================================
# ACTIVATE / DEACTIVATE
# ===================================
async def activate_product(product_id: str):
    await execute(
        queries["product"]["activate"],
        {"id": product_id}
    )
    return await get_product_by_id(product_id)


async def deactivate_product(product_id: str):
    await execute(
        queries["product"]["deactivate"],
        {"id": product_id}
    )
    return await get_product_by_id(product_id)
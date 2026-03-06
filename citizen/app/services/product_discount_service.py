from datetime import datetime
from app.domain.product_discount_domain import ProductDiscount
from app.core.database import execute, query, query_all
from app.utils.query_loader import load_queries

queries = load_queries()


# ---------------- CREATE ----------------

async def create_product_discount(discount: ProductDiscount):
    await execute(
        queries["product_discount"]["create"],
        discount.to_dict()
    )
    return await get_product_discount_by_id(discount.id)


# ---------------- GET ALL ----------------

async def get_all_product_discounts():
    return await query_all(
        queries["product_discount"]["get_all"]
    )


async def get_all_product_discounts_active():
    return await query_all(
        queries["product_discount"]["get_all_active"]
    )


# ---------------- GET BY ID ----------------

async def get_product_discount_by_id(id: str):
    return await query(
        queries["product_discount"]["get_by_id"],
        {"id": id}
    )


# ---------------- GET BY PRODUCT ----------------

async def get_product_discounts_by_product(product_id: str):
    return await query_all(
        queries["product_discount"]["get_by_product"],
        {"product_id": product_id}
    )


# ---------------- UPDATE ----------------

async def update_product_discount(id: str, discount: ProductDiscount):
    await execute(
        queries["product_discount"]["update"],
        {**discount.to_dict(), "id": id}
    )
    return await get_product_discount_by_id(id)


# ---------------- SOFT DELETE ----------------

async def delete_product_discount(id: str):
    await execute(
        queries["product_discount"]["soft_delete"],
        {"id": id}
    )
    return {"message": "Product Discount deleted successfully"}


# ---------------- ACTIVATE ----------------

async def activate_product_discount(id: str):
    await execute(
        queries["product_discount"]["activate"],
        {"id": id}
    )
    return await get_product_discount_by_id(id)


# ---------------- DEACTIVATE ----------------

async def deactivate_product_discount(id: str):
    await execute(
        queries["product_discount"]["deactivate"],
        {"id": id}
    )
    return await get_product_discount_by_id(id)


# ---------------- DATE RANGE ----------------

async def get_product_discounts_by_date_range(start_date: datetime, end_date: datetime):
    return await query_all(
        queries["product_discount"]["get_by_date_range"],
        {"start_date": start_date, "end_date": end_date}
    )
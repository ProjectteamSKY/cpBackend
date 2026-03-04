from app.domain.product_variant_domain import ProductVariant
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


async def create_product_variant(variant: ProductVariant):
    await execute(
        queries["product_variant"]["create"],
        variant.to_dict()
    )
    return await get_product_variant_by_id(variant.id)


async def get_all_product_variants():
    result = await query_all(
        queries["product_variant"]["get_all"]
    )
    return result


async def get_product_variant_by_id(id: str):
    return await query(
        queries["product_variant"]["get_by_id"],
        {"id": id}
    )


async def get_product_variants_by_product(product_id: str):
    return await query_all(
        queries["product_variant"]["get_by_product"],
        {"product_id": product_id}
    )


async def update_product_variant(id: str, variant: ProductVariant):
    await execute(
        queries["product_variant"]["update"],
        {**variant.to_dict(), "id": id}
    )
    return await get_product_variant_by_id(id)


async def delete_product_variant(id: str):
    await execute(
        queries["product_variant"]["soft_delete"],
        {"id": id}
    )
    return {"message": "Product Variant deleted successfully"}


async def activate_product_variant(id: str):
    await execute(
        queries["product_variant"]["activate"],
        {"id": id}
    )
    return await get_product_variant_by_id(id)
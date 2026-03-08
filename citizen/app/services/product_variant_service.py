from typing import Optional

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



async def calculate_variant_weight(variant_id: str, quantity: int) -> Optional[float]:
    """
    Calculate total weight (grams) for a product variant based on size, paper GSM, and quantity.
    """
    sql = """
    SELECT s.width, s.height, pt.gsm
    FROM product_variants pv
    LEFT JOIN sizes s ON pv.size_id = s.id
    LEFT JOIN paper_types pt ON pv.paper_type_id = pt.id
    WHERE pv.id = :variant_id;
    """
    
    variant = await query(sql, {"variant_id": variant_id})
    
    if not variant:
        return None
    
    width_mm = variant["width"]
    height_mm = variant["height"]
    gsm = variant["gsm"] or 300  # default to 300 if GSM is null
    
    # Convert mm to meters
    width_m = width_mm / 1000
    height_m = height_mm / 1000
    
    area_m2 = width_m * height_m
    
    weight_per_sheet = area_m2 * gsm  # grams per sheet
    total_weight = weight_per_sheet * quantity  # grams
    
    return round(total_weight, 2)
import json
from datetime import datetime
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
    rows = await query_all(
        queries["product"]["get_by_category"],
        {"category_id": category_id}
    )

    products_map = {}

    for row in rows:
        pid = row["product_id"]

        if pid not in products_map:
            # ✅ parse images safely
            images = row["images"]
            related_images = row["related_images"]

            if isinstance(images, str):
                images = json.loads(images)

            if isinstance(related_images, str):
                related_images = json.loads(related_images)

            images = images or []
            related_images = related_images or []

            products_map[pid] = {
                "id": pid,
                "name": row["product_name"],
                "description": row["description"],
                "category_id": row["category_id"],

                # ✅ images
                "image": images[0] if images else None,  # default
                "images": images,
                "related_images": related_images,

                "variants": []
            }

        product = products_map[pid]

        # ✅ variants
        if row["variant_id"]:
            variants = product["variants"]

            variant = next(
                (v for v in variants if v["id"] == row["variant_id"]),
                None
            )

            if not variant:
                variant = {
                    "id": row["variant_id"],
                    "size_id": row["size_id"],
                    "paper_type_id": row["paper_type_id"],
                    "print_type_id": row["print_type_id"],
                    "cut_type_id": row["cut_type_id"],
                    "sides": row["sides"],
                    "orientation": row["orientation"],
                    "prices": []
                }
                variants.append(variant)

            # prices
            if row["variant_price_id"]:
                variant["prices"].append({
                    "id": row["variant_price_id"],
                    "price": row["price"],
                    "min_qty": row["min_qty"]
                })

    return list(products_map.values())


# ===================================
#  FIXED UPDATE
# ===================================
async def update_product(product_id: str, product: Product):
    #  Ensure ALL required fields have values
    params = {
        "id": product_id,
        "updated_at": datetime.utcnow(),
        "category_id": product.category_id or None,
        "subcategory_id": product.subcategory_id or None,
        "name": product.name or "",
        "sku": getattr(product, 'sku', None) or "",  #  Critical fix
        "description": product.description or None,
        "min_order_qty": product.min_order_qty or 100,
        "max_order_qty": product.max_order_qty or None,
        "images": json.dumps(product.images or []),
        "related_images": json.dumps(product.related_images or []),
    }
    
    result = await execute(
        queries["product"]["update"],
        params
    )
    
    await get_product_by_id(product_id)
    return result


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



async def get_product_list_minimal():
    products = await query_all(queries["product"]["get_all_active"])

    result = []

    for p in products:
        images = []

        if p.get("images"):
            try:
                images = json.loads(p["images"])
            except:
                images = []

        main_image = None

        for img in images:
            #  CASE 1: dict format
            if isinstance(img, dict):
                if img.get("is_default"):
                    main_image = img.get("url")
                    break

            #  CASE 2: string format
            elif isinstance(img, str):
                main_image = img
                break

        #  fallback
        if not main_image and images:
            first = images[0]
            if isinstance(first, dict):
                main_image = first.get("url")
            elif isinstance(first, str):
                main_image = first

        result.append({
            "id": p["id"],
            "name": p["name"],
            "image": main_image
        })

    return result


async def get_products_by_subcategory(subcategory_id: str):
    rows = await query_all(
        queries["product"]["get_by_subcategory"],
        {"subcategory_id": subcategory_id}
    )

    products_map = {}

    for row in rows:
        pid = row["product_id"]

        if pid not in products_map:
            # ✅ parse images safely
            images = row["images"]
            related_images = row["related_images"]

            if isinstance(images, str):
                images = json.loads(images)

            if isinstance(related_images, str):
                related_images = json.loads(related_images)

            images = images or []
            related_images = related_images or []

            products_map[pid] = {
                "id": pid,
                "name": row["product_name"],
                "description": row["description"],
                "category_id": row["category_id"],
                "subcategory_id": row["subcategory_id"],

                # ✅ images
                "image": images[0] if images else None,
                "images": images,
                "related_images": related_images,

                "variants": []
            }

        product = products_map[pid]

        # ✅ variants
        if row["variant_id"]:
            variants = product["variants"]

            variant = next(
                (v for v in variants if v["id"] == row["variant_id"]),
                None
            )

            if not variant:
                variant = {
                    "id": row["variant_id"],
                    "size_id": row["size_id"],
                    "paper_type_id": row["paper_type_id"],
                    "print_type_id": row["print_type_id"],
                    "cut_type_id": row["cut_type_id"],
                    "sides": row["sides"],
                    "orientation": row["orientation"],
                    "prices": []
                }
                variants.append(variant)

            # ✅ prices
            if row["variant_price_id"]:
                variant["prices"].append({
                    "id": row["variant_price_id"],
                    "price": row["price"],
                    "min_qty": row["min_qty"]
                })

    return list(products_map.values())


async def get_products_by_subcategory_minimal(subcategory_id: str):
    rows = await query_all(
        queries["product"]["get_by_subcategory_minimal"],
        {"subcategory_id": subcategory_id}
    )

    return [
        {
            "id": row["id"],
            "name": row["name"]
        }
        for row in rows
    ]
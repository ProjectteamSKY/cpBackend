# SERVICE FILE (Complete)
from datetime import datetime
import os
import uuid
import json
import re
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.utils.query_loader import load_queries
from app.domain.productsetup_domain import ProductSetup
from app.core.database import execute, query, query_all
from app.services.product_variant_service import delete_product_variant
from app.services.product_variant_price_service import soft_delete_product_variant_price

# Create upload folder if not exists
UPLOAD_FOLDER = "media/products"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load SQL templates from TOML
queries = load_queries()

async def generate_sku(name: str) -> str:
    """
    Generate SKU from product name
    Format: First 3 letters (UPPER) + Random 6 chars
    Example: "Business Card" -> "BUS-ABC123"
    """
    # Clean and take first 3 letters, uppercase
    clean_name = re.sub(r'[^a-zA-Z\s]', '', name).strip()
    name_prefix = ''.join(clean_name.split()[:1])[:3].upper()
    
    # Generate random part
    random_part = uuid.uuid4().hex[:6].upper()
    
    return f"{name_prefix}-{random_part}"

async def create_productsetup(data: ProductSetup):
    product_id = data.product_id or str(uuid.uuid4())
    data.product_id = product_id

    # ✅ FIXED: Use generated SKU from data.sku
    sku = getattr(data, 'sku', await generate_sku(data.name))

    product_params = {
        "id": product_id,
        "sku": sku,  # ✅ Now properly provided
        "category_id": data.category_id,
        "subcategory_id": data.subcategory_id,
        "name": data.name,
        "description": data.description,
        "min_order_qty": data.min_order_qty,
        "max_order_qty": data.max_order_qty,
        "images": json.dumps([img.model_dump() for img in data.images]),
        "related_images": json.dumps([img.model_dump() for img in data.related_images]),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    # Insert Product
    await execute(queries["product"]["create"], product_params)

    # Insert Variants
    for variant in data.variants:
        variant_id = variant.id or str(uuid.uuid4())

        variant_params = {
            "id": variant_id,
            "product_id": product_id,
            "size_id": variant.size_id,
            "paper_type_id": variant.paper_type_id,
            "print_type_id": variant.print_type_id,
            "cut_type_id": variant.cut_type_id,
            "sides": variant.sides,
            "two_side_cut": variant.two_side_cut,
            "four_side_cut": variant.four_side_cut,
            "orientation": variant.orientation,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await execute(queries["product_variant"]["create"], variant_params)

        # Insert Prices
        for price in variant.prices:
            price_id = price.id or str(uuid.uuid4())
            discount_id = None

            if price.discount:
                discount_id = price.discount.id or str(uuid.uuid4())

                discount_params = {
                    "id": discount_id,
                    "product_id": product_id,
                    "description": price.discount.description,
                    "discount": price.discount.discount,
                    "start_date": price.discount.start_date,
                    "end_date": price.discount.end_date,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }

                await execute(
                    queries["product_discount"]["create"],
                    discount_params
                )

            price_params = {
                "id": price_id,
                "variant_id": variant_id,
                "discount_id": discount_id,
                "min_qty": price.min_qty,
                "price": price.price,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            await execute(
                queries["product_variant_price"]["create"],
                price_params
            )

    return {"status": "success", "product_id": product_id}


import json

def normalize_images(images):
    """Convert DB image string → clean uniform structure"""
    if not images:
        return []

    try:
        parsed = json.loads(images) if isinstance(images, str) else images
    except Exception:
        return []

    normalized = []

    for img in parsed:
        url = (
            img.get("url") or
            (img.get("original") or {}).get("url") or
            (img.get("mobile") or {}).get("url") or
            (img.get("thumbnail") or {}).get("url")
        )

        if url:
            normalized.append({
                "id": img.get("id"),
                "url": url,
                "is_default": img.get("is_default", False)
            })

    return normalized




async def get_product_by_id(product_id: str):
    """Fetch product with variants, prices, and discounts"""

    # 1️⃣ Fetch product
    product = await query(
        queries["product"]["get_by_id"],
        {"id": product_id}
    )

    if not product:
        return None

    product_dict = dict(product)

    # ✅ FIX: Normalize images here
    product_dict["images"] = normalize_images(product_dict.get("images"))
    product_dict["related_images"] = normalize_images(product_dict.get("related_images"))

    # 2️⃣ Fetch variants
    variants = await query_all(
        queries["product_variant"]["get_by_product"],
        {"product_id": product_id}
    )

    variant_list = []

    for v in variants:
        v_dict = dict(v)

        # 3️⃣ Fetch prices
        prices = await query_all(
            queries["product_variant_price"]["get_by_variant"],
            {"variant_id": v_dict["id"]}
        )

        price_list = []

        for p in prices:
            p_dict = dict(p)

            # 4️⃣ Fetch discount
            discount_id = p_dict.get("discount_id")

            if discount_id:
                discount = await query(
                    queries["product_discount"]["get_by_id"],
                    {"id": discount_id}
                )
                p_dict["discount"] = dict(discount) if discount else None
            else:
                p_dict["discount"] = None

            price_list.append(p_dict)

        v_dict["prices"] = price_list
        variant_list.append(v_dict)

    product_dict["variants"] = variant_list

    return product_dict

async def get_all_products_with_details():
    """
    Fetch all products with variants, prices, and discounts
    """

    # 1️⃣ Fetch all products
    products = await query_all(
        queries["product"]["get_all_active"]
    )

    product_list = []

    for product in products:
        product_dict = dict(product)
        product_id = product_dict["id"]

        # 2️⃣ Fetch variants
        variants = await query_all(
            queries["product_variant"]["get_by_product"],
            {"product_id": product_id}
        )

        variant_list = []

        for v in variants:
            v_dict = dict(v)
            variant_id = v_dict["id"]

            # 3️⃣ Fetch prices
            prices = await query_all(
                queries["product_variant_price"]["get_by_variant"],
                {"variant_id": variant_id}
            )

            price_list = []

            for p in prices:
                p_dict = dict(p)

                # 4️⃣ Fetch discount
                discount_id = p_dict.get("discount_id")

                if discount_id:
                    discount = await query(
                        queries["product_discount"]["get_by_id"],
                        {"id": discount_id}
                    )
                    p_dict["discount"] = dict(discount) if discount else None
                else:
                    p_dict["discount"] = None

                price_list.append(p_dict)

            v_dict["prices"] = price_list
            variant_list.append(v_dict)

        product_dict["variants"] = variant_list
        product_list.append(product_dict)

    return product_list

async def update_productsetup(product_id: str, data: dict):

    try:
        # ================= PRODUCT UPDATE =================
        await execute(
            queries["product"]["update"],
            {
                "id": product_id,
                "category_id": data.get("category_id"),
                "subcategory_id": data.get("subcategory_id"),
                "name": data.get("name"),
                "sku": data.get("sku"),  # ✅ FIX
                "description": data.get("description"),
                "min_order_qty": data.get("min_order_qty"),
                "max_order_qty": data.get("max_order_qty"),

                # ✅ FIX: convert list → JSON
                "images": json.dumps(data.get("images")) if data.get("images") else None,
                "related_images": json.dumps(data.get("related_images")) if data.get("related_images") else None,

                "updated_at": datetime.utcnow(),
            }
        )

        # ================= VARIANTS =================
        for variant in data.get("variants", []):

            # ---------- CREATE OR UPDATE VARIANT ----------
            if variant.get("id"):
                variant_id = variant["id"]

                await execute(
                    queries["product_variant"]["update"],
                    {
                        "id": variant_id,
                        "product_id": product_id,
                        "size_id": variant.get("size_id"),
                        "paper_type_id": variant.get("paper_type_id"),
                        "print_type_id": variant.get("print_type_id"),
                        "cut_type_id": variant.get("cut_type_id"),
                        "sides": variant.get("sides"),
                        "two_side_cut": variant.get("two_side_cut"),
                        "four_side_cut": variant.get("four_side_cut"),
                        "orientation": variant.get("orientation"),
                        "is_active": variant.get("is_active", True),  # ✅ FIX
                        "updated_at": datetime.utcnow(),
                    }
                )

            else:
                variant_id = str(uuid.uuid4())

                await execute(
                    queries["product_variant"]["create"],
                    {
                        "id": variant_id,
                        "product_id": product_id,
                        "size_id": variant.get("size_id"),
                        "paper_type_id": variant.get("paper_type_id"),
                        "print_type_id": variant.get("print_type_id"),
                        "cut_type_id": variant.get("cut_type_id"),
                        "sides": variant.get("sides"),
                        "two_side_cut": variant.get("two_side_cut"),
                        "four_side_cut": variant.get("four_side_cut"),
                        "orientation": variant.get("orientation"),
                        "is_active": True,  # ✅ REQUIRED
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }
                )

            # ================= PRICES =================
            for price in variant.get("prices", []):

                # ---------- UPDATE PRICE ----------
                if price.get("id"):
                    price_id = price["id"]
                    discount_id = None

                    # ===== DISCOUNT =====
                    if price.get("discount"):
                        discount = price["discount"]

                        if discount.get("id"):
                            discount_id = discount["id"]

                            await execute(
                                queries["product_discount"]["update"],
                                {
                                    "id": discount_id,
                                    "product_id": product_id,
                                    "description": discount.get("description"),
                                    "discount": discount.get("discount"),
                                    "start_date": discount.get("start_date"),
                                    "end_date": discount.get("end_date"),
                                    "updated_at": datetime.utcnow(),
                                }
                            )
                        else:
                            discount_id = str(uuid.uuid4())

                            await execute(
                                queries["product_discount"]["create"],
                                {
                                    "id": discount_id,
                                    "product_id": product_id,
                                    "description": discount.get("description"),
                                    "discount": discount.get("discount"),
                                    "start_date": discount.get("start_date"),
                                    "end_date": discount.get("end_date"),
                                    "created_at": datetime.utcnow(),
                                    "updated_at": datetime.utcnow(),
                                }
                            )

                    await execute(
                        queries["product_variant_price"]["update"],
                        {
                            "id": price_id,
                            "variant_id": variant_id,
                            "discount_id": discount_id,
                            "min_qty": price.get("min_qty"),
                            "price": price.get("price"),
                            "is_active": price.get("is_active", True),  # ✅ FIX
                            "updated_at": datetime.utcnow(),
                        }
                    )

                # ---------- CREATE PRICE ----------
                else:
                    price_id = str(uuid.uuid4())
                    discount_id = None

                    if price.get("discount"):
                        discount = price["discount"]

                        discount_id = str(uuid.uuid4())

                        await execute(
                            queries["product_discount"]["create"],
                            {
                                "id": discount_id,
                                "product_id": product_id,
                                "description": discount.get("description"),
                                "discount": discount.get("discount"),
                                "start_date": discount.get("start_date"),
                                "end_date": discount.get("end_date"),
                                "created_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow(),
                            }
                        )

                    await execute(
                        queries["product_variant_price"]["create"],
                        {
                            "id": price_id,
                            "variant_id": variant_id,
                            "discount_id": discount_id,
                            "min_qty": price.get("min_qty"),
                            "price": price.get("price"),
                            "is_active": True,  # ✅ FIX
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                        }
                    )

        # ✅ FINAL RETURN FIX
        return {
            "status": "success",
            "message": "Product updated successfully",
            "product_id": product_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def soft_delete_product_setup_service(id: str, type: str):
    try:

        # ================= DELETE VARIANT =================
        if type == "variant":

            # 🔥 delete all prices under this variant
            prices = await query_all(
                queries["product_variant_price"]["get_by_variant"],
                {"variant_id": id}
            )

            for price in prices:
                await soft_delete_product_variant_price(price["id"])

            # 🔥 delete variant
            await delete_product_variant(id)

            return {
                "status": "success",
                "message": "Variant and its prices deleted successfully",
                "variant_id": id
            }

        # ================= DELETE PRICE =================
        elif type == "price":

            await soft_delete_product_variant_price(id)

            return {
                "status": "success",
                "message": "Price deleted successfully",
                "price_id": id
            }

        # ================= INVALID TYPE =================
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid type. Use 'variant' or 'price'"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def delete_productsetup(product_id: str):
    """
    Soft delete a product, its variants, prices, and discounts.
    Marks `is_deleted = TRUE` and `is_active = FALSE` where applicable.
    """
    try:
        # 1️⃣ Check if product exists
        product = await query(
            queries["product"]["get_by_id"],
            {"id": product_id}
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 2️⃣ Soft delete the product
        await execute(
            queries["product"]["delete"],
            {"id": product_id}
        )

        # 3️⃣ Fetch and soft delete all variants
        variants = await query_all(
            queries["product_variant"]["get_by_product"],
            {"product_id": product_id}
        )

        for v in variants:
            variant_id = v["id"]
            await execute(
                queries["product_variant"]["soft_delete"],
                {"id": variant_id}
            )

            # 4️⃣ Soft delete all prices for this variant
            prices = await query_all(
                queries["product_variant_price"]["get_by_variant"],
                {"variant_id": variant_id}
            )

            for p in prices:
                price_id = p["id"]
                await execute(
                    queries["product_variant_price"]["soft_delete"],
                    {"id": price_id}
                )

                # 5️⃣ Soft delete discount if exists
                discount_id = p.get("discount_id")
                if discount_id:
                    await execute(
                        queries["product_discount"]["soft_delete"],
                        {"id": discount_id}
                    )

        return {
            "status": "success",
            "message": "Product deleted successfully",
            "product_id": product_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
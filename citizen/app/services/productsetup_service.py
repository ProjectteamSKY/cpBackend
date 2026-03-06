from datetime import datetime
import os
import uuid
import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.utils.query_loader import load_queries
from app.domain.productsetup_domain import ProductSetup
from app.core.database import execute, query, query_all

# Create upload folder if not exists
UPLOAD_FOLDER = "media/products"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load SQL templates from TOML
queries = load_queries()


async def create_productsetup(data: ProductSetup):
    product_id = data.product_id or str(uuid.uuid4())
    data.product_id = product_id

    product_params = {
        "id": product_id,
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

    # 2️⃣ Fetch variants
    variants = await query_all(
        queries["product_variant"]["get_by_product"],
        {"product_id": product_id}
    )

    variant_list = []

    for v in variants:
        v_dict = dict(v)

        # 3️⃣ Fetch prices for this variant
        prices = await query_all(
            queries["product_variant_price"]["get_by_variant"],
            {"variant_id": v_dict["id"]}
        )

        price_list = []

        for p in prices:
            p_dict = dict(p)

            # 4️⃣ Fetch discount if exists
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

    await execute(
        queries["product"]["update"],
        {
            "id": product_id,
            "category_id": data["category_id"],
            "subcategory_id": data["subcategory_id"],
            "name": data["name"],
            "description": data["description"],
            "min_order_qty": data["min_order_qty"],
            "max_order_qty": data["max_order_qty"],
            "images": json.dumps(data["images"]),
            "related_images": json.dumps(data["related_images"]),
            "updated_at": datetime.utcnow(),
        }
    )

    for variant in data["variants"]:

        if not variant.get("id"):
            raise HTTPException(status_code=400, detail="Variant ID required")

        await execute(
            queries["product_variant"]["update"],
            {
                "id": variant["id"],
                "product_id": product_id,
                "size_id": variant.get("size_id"),
                "paper_type_id": variant.get("paper_type_id"),
                "print_type_id": variant.get("print_type_id"),
                "cut_type_id": variant.get("cut_type_id"),
                "sides": variant.get("sides"),
                "two_side_cut": variant.get("two_side_cut"),
                "four_side_cut": variant.get("four_side_cut"),
                "orientation": variant.get("orientation"),
                "updated_at": datetime.utcnow(),
            }
        )

        for price in variant.get("prices", []):

            if not price.get("id"):
                raise HTTPException(status_code=400, detail="Price ID required")

            discount_id = None

            if price.get("discount"):
                discount = price["discount"]

                if not discount.get("id"):
                    raise HTTPException(status_code=400, detail="Discount ID required")

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

            await execute(
                queries["product_variant_price"]["update"],
                {
                    "id": price["id"],
                    "variant_id": variant["id"],
                    "discount_id": discount_id,
                    "min_qty": price.get("min_qty"),
                    "price": price.get("price"),
                    "is_active": price.get("is_active"),
                    "updated_at": datetime.utcnow(),
                }
            )

    return {"status": "success", "product_id": product_id}
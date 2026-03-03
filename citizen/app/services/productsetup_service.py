from datetime import datetime
import os
import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.utils.query_loader import load_queries
from app.domain.productsetup_domain import ProductSetup

# Create upload folder if not exists
UPLOAD_FOLDER = "media/products"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load SQL templates from TOML
queries = load_queries()


async def create_productsetup(data: ProductSetup, session: AsyncSession):
    """
    Create product with variants, prices, and optional discounts.
    """

    # Generate product ID if missing
    product_id = data.product_id or str(uuid.uuid4())
    data.product_id = product_id

    # 1️⃣ Prepare product parameters
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

    async with session.begin():  # single transaction

        # Insert product
        await session.execute(
            text(queries["product"]["create"]),
            product_params
        )

        # 2️⃣ Insert product variants
        for variant in data.variants or []:
            variant.id = variant.id or str(uuid.uuid4())
            variant_params = {
                "id": variant.id,
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
            await session.execute(
                text(queries["product_variant"]["create"]),
                variant_params
            )

            # 3️⃣ Insert product variant prices
            for price in variant.prices or []:
                price.id = price.id or str(uuid.uuid4())

                # Insert discount first if exists
                discount_id = None
                if getattr(price, "discount", None):
                    discount = price.discount
                    discount.id = discount.id or str(uuid.uuid4())
                    discount_id = discount.id

                    discount_params = {
                        "id": discount.id,
                        "product_id": product_id,
                        "description": discount.description,
                        "discount": discount.discount,
                        "start_date": discount.start_date,
                        "end_date": discount.end_date,
                        "is_active": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }

                    await session.execute(
                        text(queries["product_discount"]["create"]),
                        discount_params
                    )

                # Insert price row
                price_params = {
                    "id": price.id,
                    "variant_id": variant.id,
                    "discount_id": discount_id,  # can be None
                    "min_qty": price.min_qty,
                    "max_qty": price.max_qty,
                    "price": price.price,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }

                await session.execute(
                    text(queries["product_variant_price"]["create"]),
                    price_params
                )

    return {"status": "success", "product_id": product_id}


async def get_product_by_id(product_id: str, session: AsyncSession):
    """Fetch product with variants, prices, and discounts"""

    # 1️⃣ Fetch product
    product_query = text(queries["product"]["get_by_id"])
    product_result = await session.execute(product_query, {"id": product_id})
    product = product_result.mappings().first()
    if not product:
        return None
    product_dict = dict(product)

    # 2️⃣ Fetch variants
    variant_query = text(queries["product_variant"]["get_by_product"])
    variant_result = await session.execute(variant_query, {"product_id": product_id})
    variants = variant_result.mappings().all()
    variant_list = []

    for v in variants:
        v_dict = dict(v)

        # 3️⃣ Fetch prices for this variant
        price_query = text(queries["product_variant_price"]["get_by_variant"])
        price_result = await session.execute(price_query, {"variant_id": v_dict["id"]})
        prices = price_result.mappings().all()
        price_list = []

        for p in prices:
            p_dict = dict(p)

            # 4️⃣ Fetch discount if exists
            discount_id = p_dict.get("discount_id")
            if discount_id:
                discount_query = text(queries["product_discount"]["get_by_id"])
                discount_result = await session.execute(discount_query, {"id": discount_id})
                discount = discount_result.mappings().first()
                p_dict["discount"] = dict(discount) if discount else None
            else:
                p_dict["discount"] = None

            price_list.append(p_dict)

        v_dict["prices"] = price_list
        variant_list.append(v_dict)

    product_dict["variants"] = variant_list
    return product_dict


async def get_all_products_with_details(session: AsyncSession):
    """
    Fetch all products with variants, prices, and discounts
    """

    # 1️⃣ Fetch all products
    product_query = text(queries["product"]["get_all_active"])
    product_result = await session.execute(product_query)
    products = product_result.mappings().all()

    product_list = []

    for product in products:
        product_dict = dict(product)
        product_id = product_dict["id"]

        # 2️⃣ Fetch variants for product
        variant_query = text(queries["product_variant"]["get_by_product"])
        variant_result = await session.execute(
            variant_query,
            {"product_id": product_id}
        )
        variants = variant_result.mappings().all()

        variant_list = []

        for v in variants:
            v_dict = dict(v)
            variant_id = v_dict["id"]

            # 3️⃣ Fetch prices
            price_query = text(queries["product_variant_price"]["get_by_variant"])
            price_result = await session.execute(
                price_query,
                {"variant_id": variant_id}
            )
            prices = price_result.mappings().all()

            price_list = []

            for p in prices:
                p_dict = dict(p)

                # 4️⃣ Fetch discount
                discount_id = p_dict.get("discount_id")
                if discount_id:
                    discount_query = text(queries["product_discount"]["get_by_id"])
                    discount_result = await session.execute(
                        discount_query,
                        {"id": discount_id}
                    )
                    discount = discount_result.mappings().first()
                    p_dict["discount"] = dict(discount) if discount else None
                else:
                    p_dict["discount"] = None

                price_list.append(p_dict)

            v_dict["prices"] = price_list
            variant_list.append(v_dict)

        product_dict["variants"] = variant_list
        product_list.append(product_dict)

    return product_list
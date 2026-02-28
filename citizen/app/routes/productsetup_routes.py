from datetime import datetime
import json
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.productsetup_domain import ProductSetup
from app.utils.query_loader import load_queries

import os
import uuid

from app.services.productsetup_service import get_product_by_id , get_all_products_with_details

router = APIRouter()

UPLOAD_FOLDER = "media/products"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

queries = load_queries()

# ---------------------------------------------------
# File upload helper
# ---------------------------------------------------

def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return path.replace("\\", "/")


def process_files(files: Optional[List[UploadFile]], include_default=False):
    results = []

    if files:
        for index, file in enumerate(files):
            path = save_upload(file)

            data = {
                "id": str(uuid.uuid4()),
                "url": path,
            }

            if include_default:
                data["is_default"] = index == 0  # first image default

            results.append(data)

    return results


# ---------------------------------------------------
# Core creation logic
# ---------------------------------------------------

async def create_productsetup(data: ProductSetup, session: AsyncSession):
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

    async with session.begin():

        # Insert Product
        await session.execute(text(queries["product"]["create"]), product_params)

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

            await session.execute(text(queries["product_variant"]["create"]), variant_params)

            # Insert Prices
            for price in variant.prices:
                price_id = price.id or str(uuid.uuid4())
                discount_id = None

                # Insert Discount if exists
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

                    await session.execute(
                        text(queries["product_discount"]["create"]),
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

                await session.execute(
                    text(queries["product_variant_price"]["create"]),
                    price_params
                )

    return {"status": "success", "product_id": product_id}


# ---------------------------------------------------
# API Endpoint
# ---------------------------------------------------

@router.post("/create")
async def create_product_endpoint(
    category_id: str = Form(...),
    subcategory_id: Optional[str] = Form(None),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    min_order_qty: int = Form(...),
    max_order_qty: Optional[int] = Form(None),
    variants: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    related_images: Optional[List[UploadFile]] = File(None),
    session: AsyncSession = Depends(get_session),
):
    try:
        variants_data = json.loads(variants)
    except Exception:
        raise HTTPException(status_code=400, detail="Variants must be valid JSON")

    # Process files properly
    saved_images = process_files(images, include_default=True)
    saved_related_images = process_files(related_images)

    # Create ProductSetup model (VALID STRUCTURE)
    product = ProductSetup(
        category_id=category_id,
        subcategory_id=subcategory_id,
        name=name,
        description=description,
        min_order_qty=min_order_qty,
        max_order_qty=max_order_qty,
        images=saved_images,
        related_images=saved_related_images,
        variants=variants_data,
    )

    result = await create_productsetup(product, session)

    return {
        "status": "success",
        "product_id": result["product_id"],
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "name": name,
        "description": description,
        "min_order_qty": min_order_qty,
        "max_order_qty": max_order_qty,
        "images": saved_images,
        "related_images": saved_related_images,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
@router.get("/products/{product_id}")
async def get_product(product_id: str, session: AsyncSession = Depends(get_session)):
    """
    Get product details including variants, prices, and discounts
    """
    product = await get_product_by_id(product_id, session)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"status": "success", "product": product}


@router.get("/list")
async def get_all_products(session: AsyncSession = Depends(get_session)):
    """
    Get all products with variants, prices and discounts
    """
    products = await get_all_products_with_details(session)

    return {
        "status": "success",
        "count": len(products),
        "products": products
    }


# async def update_productsetup(product_id: str, data: ProductSetup, session: AsyncSession):
#     existing_product = await get_product_by_id(product_id, session)
#     if not existing_product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     # Update main product
#     product_params = {
#         "id": product_id,
#         "category_id": data.category_id,
#         "subcategory_id": data.subcategory_id,
#         "name": data.name,
#         "description": data.description,
#         "min_order_qty": data.min_order_qty,
#         "max_order_qty": data.max_order_qty,
#         "images": json.dumps([img.model_dump() for img in data.images]),
#         "related_images": json.dumps([img.model_dump() for img in data.related_images]),
#         "updated_at": datetime.utcnow(),
#     }

#     async with session.begin():
#         # Update product table
#         await session.execute(text(queries["product"]["update_by_id"]), product_params)

#         # Update variants
#         for variant in data.variants:
#             variant_id = variant.id or str(uuid.uuid4())

#             # Check if variant exists
#             variant_exists = any(v["id"] == variant_id for v in existing_product["variants"])
#             variant_params = {
#                 "id": variant_id,
#                 "product_id": product_id,
#                 "size_id": variant.size_id,
#                 "paper_type_id": variant.paper_type_id,
#                 "print_type_id": variant.print_type_id,
#                 "cut_type_id": variant.cut_type_id,
#                 "sides": variant.sides,
#                 "two_side_cut": variant.two_side_cut,
#                 "four_side_cut": variant.four_side_cut,
#                 "orientation": variant.orientation,
#                 "is_active": True,
#                 "updated_at": datetime.utcnow(),
#             }

#             if variant_exists:
#                 await session.execute(text(queries["product_variant"]["update_by_id"]), variant_params)
#             else:
#                 variant_params["created_at"] = datetime.utcnow()
#                 await session.execute(text(queries["product_variant"]["create"]), variant_params)

#             # Update prices
#             for price in variant.prices:
#                 price_id = price.id or str(uuid.uuid4())
#                 discount_id = None

#                 if price.discount:
#                     discount_id = price.discount.id or str(uuid.uuid4())
#                     discount_params = {
#                         "id": discount_id,
#                         "product_id": product_id,
#                         "description": price.discount.description,
#                         "discount": price.discount.discount,
#                         "start_date": price.discount.start_date,
#                         "end_date": price.discount.end_date,
#                         "is_active": True,
#                         "updated_at": datetime.utcnow(),
#                     }
#                     await session.execute(
#                         text(queries["product_discount"].get("update_by_id") or queries["product_discount"]["create"]),
#                         discount_params
#                     )

#                 price_params = {
#                     "id": price_id,
#                     "variant_id": variant_id,
#                     "discount_id": discount_id,
#                     "min_qty": price.min_qty,
#                     "max_qty": price.max_qty,
#                     "price": price.price,
#                     "is_active": True,
#                     "updated_at": datetime.utcnow(),
#                 }

#                 # Check if price exists
#                 variant_existing = next((v for v in existing_product["variants"] if v["id"] == variant_id), {})
#                 price_exists = any(p["id"] == price_id for p in variant_existing.get("prices", []))
#                 if price_exists:
#                     await session.execute(text(queries["product_variant_price"]["update_by_id"]), price_params)
#                 else:
#                     price_params["created_at"] = datetime.utcnow()
#                     await session.execute(text(queries["product_variant_price"]["create"]), price_params)

#     return {"status": "success", "product_id": product_id}

# -------------------------
# Update endpoint
# -------------------------
# @router.put("/update/{product_id}")
# async def update_product_endpoint(
#     product_id: str,
#     category_id: str = Form(...),
#     subcategory_id: Optional[str] = Form(None),
#     name: str = Form(...),
#     description: Optional[str] = Form(None),
#     min_order_qty: int = Form(...),
#     max_order_qty: Optional[int] = Form(None),
#     variants: str = Form(...),
#     images: Optional[List[UploadFile]] = File(None),
#     related_images: Optional[List[UploadFile]] = File(None),
#     session: AsyncSession = Depends(get_session),
# ):
#     try:
#         variants_data = json.loads(variants)
#     except Exception:
#         raise HTTPException(status_code=400, detail="Variants must be valid JSON")

#     # Fetch existing product
#     existing_product = await get_product_by_id(product_id, session)
#     if not existing_product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     # Handle file uploads
#     saved_images = process_files(images, include_default=True) if images else json.loads(existing_product["images"])
#     saved_related_images = process_files(related_images) if related_images else json.loads(existing_product["related_images"])

#     # Prepare product update params
#     product_params = {
#         "id": product_id,
#         "category_id": category_id,
#         "subcategory_id": subcategory_id,
#         "name": name,
#         "description": description,
#         "min_order_qty": min_order_qty,
#         "max_order_qty": max_order_qty,
#         "images": json.dumps(saved_images),
#         "related_images": json.dumps(saved_related_images),
#         "updated_at": datetime.utcnow(),
#     }

#     # Update product
#     await session.execute(text(queries["product"]["update"]), product_params)

#     # Update or create variants
#     for variant in variants_data:
#         variant_id = variant.get("id")
#         existing_variant = None
#         if variant_id:
#             existing_variant = next((v for v in existing_product.get("variants", []) if v["id"] == variant_id), None)

#         # Prepare variant params
#         variant_params = {
#             "id": variant_id or str(uuid.uuid4()),
#             "product_id": product_id,
#             "size_id": variant.get("size_id"),
#             "paper_type_id": variant.get("paper_type_id"),
#             "print_type_id": variant.get("print_type_id"),
#             "cut_type_id": variant.get("cut_type_id"),
#             "sides": variant.get("sides"),
#             "two_side_cut": variant.get("two_side_cut"),
#             "four_side_cut": variant.get("four_side_cut"),
#             "orientation": variant.get("orientation"),
#             "is_active": True,
#             "updated_at": datetime.utcnow(),
#         }

#         if existing_variant:
#             await session.execute(text(queries["product_variant"]["update_by_id"]), variant_params)
#         else:
#             variant_params["created_at"] = datetime.utcnow()
#             await session.execute(text(queries["product_variant"]["create"]), variant_params)

#         # Update or create prices
#         for price in variant.get("prices", []):
#             price_id = price.get("id")
#             existing_price = None
#             if existing_variant and price_id:
#                 existing_price = next(
#                     (p for p in existing_variant.get("prices", []) if p["id"] == price_id),
#                     None
#                 )

#             price_params = {
#                 "id": price_id or str(uuid.uuid4()),
#                 "variant_id": variant_params["id"],
#                 "discount_id": price.get("discount", {}).get("id") if price.get("discount") else None,
#                 "min_qty": price.get("min_qty"),
#                 "max_qty": price.get("max_qty"),
#                 "price": price.get("price"),
#                 "is_active": True,
#                 "updated_at": datetime.utcnow(),
#             }

#             if existing_price:
#                 await session.execute(text(queries["product_variant_price"]["update_by_id"]), price_params)
#             else:
#                 price_params["created_at"] = datetime.utcnow()
#                 await session.execute(text(queries["product_variant_price"]["create"]), price_params)

#     await session.commit()

#     return {
#         "status": "success",
#         "product_id": product_id,
#         "category_id": category_id,
#         "subcategory_id": subcategory_id,
#         "name": name,
#         "description": description,
#         "min_order_qty": min_order_qty,
#         "max_order_qty": max_order_qty,
#         "images": saved_images,
#         "related_images": saved_related_images,
#         "updated_at": datetime.utcnow(),
#     }


# -------------------------------
# Update Product Endpoint
# -------------------------------
@router.put("/update/{product_id}")
async def update_product_endpoint(
    product_id: str,
    category_id: str = Form(...),
    subcategory_id: Optional[str] = Form(None),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    min_order_qty: int = Form(...),
    max_order_qty: Optional[int] = Form(None),
    variants: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    related_images: Optional[List[UploadFile]] = File(None),
    session: AsyncSession = Depends(get_session),
):
    # Parse variants JSON
    try:
        variants_data = json.loads(variants)
    except Exception:
        raise HTTPException(status_code=400, detail="Variants must be valid JSON")

    # Process uploaded images
    saved_images = process_files(images, include_default=True)
    saved_related_images = process_files(related_images)

    # Build ProductSetup object
    product = ProductSetup(
        product_id=product_id,
        category_id=category_id,
        subcategory_id=subcategory_id,
        name=name,
        description=description,
        min_order_qty=min_order_qty,
        max_order_qty=max_order_qty,
        images=saved_images,
        related_images=saved_related_images,
        variants=variants_data,
    )

    # Call core update logic
    result = await update_productsetup(product_id, product, session)

    return {"status": "success", "product_id": result["product_id"]}


# ---------------------------------------------------
# Core update logic (Update-only)
# ---------------------------------------------------

async def update_productsetup(product_id: str, data: ProductSetup, session: AsyncSession):
    data.product_id = product_id  # ensure product_id is set

    # -------------------------------
    # Update Product Table
    # -------------------------------
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
        "updated_at": datetime.utcnow(),
    }

    async with session.begin():
        # Update product
        await session.execute(text(queries["product"]["update"]), product_params)

        # -------------------------------
        # Update Variants
        # -------------------------------
        for variant in data.variants:
            if not getattr(variant, "id", None):
                raise HTTPException(status_code=400, detail="Variant ID is required for update")

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
                "updated_at": datetime.utcnow(),
            }

            # Update variant only
            await session.execute(text(queries["product_variant"]["update"]), variant_params)

            # -------------------------------
            # Update Prices
            # -------------------------------
            for price in variant.prices:
                if not getattr(price, "id", None):
                    raise HTTPException(status_code=400, detail="Price ID is required for update")

                discount_id = None
                if price.discount:
                    if not getattr(price.discount, "id", None):
                        raise HTTPException(status_code=400, detail="Discount ID is required for update")
                    discount_id = price.discount.id

                    # Update discount
                    discount_params = {
                        "id": discount_id,
                        "product_id": product_id,
                        "description": price.discount.description,
                        "discount": price.discount.discount,
                        "start_date": price.discount.start_date,
                        "end_date": price.discount.end_date,
                        "updated_at": datetime.utcnow(),
                    }
                    await session.execute(text(queries["product_discount"]["update"]), discount_params)

                # Update price
                price_params = {
                    "id": price.id,
                    "variant_id": variant.id,
                    "discount_id": discount_id,
                    "min_qty": price.min_qty,
                    "price": price.price,
                    "updated_at": datetime.utcnow(),
                }
                await session.execute(text(queries["product_variant_price"]["update"]), price_params)

    return {"status": "success", "product_id": product_id}
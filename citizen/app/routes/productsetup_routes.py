# from datetime import datetime
# import json
# import shutil
# from typing import List, Optional

# from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
# from sqlalchemy import text
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.database import get_session
# from app.domain.productsetup_domain import ProductSetup
# from app.utils.query_loader import load_queries

# import os
# import uuid

# from app.services.productsetup_service import get_product_by_id , get_all_products_with_details

# router = APIRouter()

# UPLOAD_FOLDER = "media/products"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# queries = load_queries()

# # ---------------------------------------------------
# # File upload helper
# # ---------------------------------------------------

# def save_upload(file: UploadFile) -> str:
#     ext = os.path.splitext(file.filename)[1]
#     filename = f"{uuid.uuid4()}{ext}"
#     path = os.path.join(UPLOAD_FOLDER, filename)

#     with open(path, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     return path.replace("\\", "/")


# def process_files(files: Optional[List[UploadFile]], include_default=False):
#     results = []

#     if files:
#         for index, file in enumerate(files):
#             path = save_upload(file)

#             data = {
#                 "id": str(uuid.uuid4()),
#                 "url": path,
#             }

#             if include_default:
#                 data["is_default"] = index == 0  # first image default

#             results.append(data)

#     return results


# # ---------------------------------------------------
# # Core creation logic
# # ---------------------------------------------------

# async def create_productsetup(data: ProductSetup, session: AsyncSession):
#     product_id = data.product_id or str(uuid.uuid4())
#     data.product_id = product_id

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
#         "is_active": True,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow(),
#     }

#     async with session.begin():

#         # Insert Product
#         await session.execute(text(queries["product"]["create"]), product_params)

#         # Insert Variants
#         for variant in data.variants:
#             variant_id = variant.id or str(uuid.uuid4())

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
#                 "created_at": datetime.utcnow(),
#                 "updated_at": datetime.utcnow(),
#             }

#             await session.execute(text(queries["product_variant"]["create"]), variant_params)

#             # Insert Prices
#             for price in variant.prices:
#                 price_id = price.id or str(uuid.uuid4())
#                 discount_id = None

#                 # Insert Discount if exists
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
#                         "created_at": datetime.utcnow(),
#                         "updated_at": datetime.utcnow(),
#                     }

#                     await session.execute(
#                         text(queries["product_discount"]["create"]),
#                         discount_params
#                     )

#                 price_params = {
#                     "id": price_id,
#                     "variant_id": variant_id,
#                     "discount_id": discount_id,
#                     "min_qty": price.min_qty,
#                     "price": price.price,
#                     "is_active": True,
#                     "created_at": datetime.utcnow(),
#                     "updated_at": datetime.utcnow(),
#                 }

#                 await session.execute(
#                     text(queries["product_variant_price"]["create"]),
#                     price_params
#                 )

#     return {"status": "success", "product_id": product_id}


# # ---------------------------------------------------
# # API Endpoint
# # ---------------------------------------------------

# @router.post("/create")
# async def create_product_endpoint(
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

#     # Process files properly
#     saved_images = process_files(images, include_default=True)
#     saved_related_images = process_files(related_images)

#     # Create ProductSetup model (VALID STRUCTURE)
#     product = ProductSetup(
#         category_id=category_id,
#         subcategory_id=subcategory_id,
#         name=name,
#         description=description,
#         min_order_qty=min_order_qty,
#         max_order_qty=max_order_qty,
#         images=saved_images,
#         related_images=saved_related_images,
#         variants=variants_data,
#     )

#     result = await create_productsetup(product, session)

#     return {
#         "status": "success",
#         "product_id": result["product_id"],
#         "category_id": category_id,
#         "subcategory_id": subcategory_id,
#         "name": name,
#         "description": description,
#         "min_order_qty": min_order_qty,
#         "max_order_qty": max_order_qty,
#         "images": saved_images,
#         "related_images": saved_related_images,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow(),
#     }
# @router.get("/products/{product_id}")
# async def get_product(product_id: str, session: AsyncSession = Depends(get_session)):
#     """
#     Get product details including variants, prices, and discounts
#     """
#     product = await get_product_by_id(product_id, session)
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     return {"status": "success", "product": product}


# @router.get("/list")
# async def get_all_products(session: AsyncSession = Depends(get_session)):
#     """
#     Get all products with variants, prices and discounts
#     """
#     products = await get_all_products_with_details(session)

#     return {
#         "status": "success",
#         "count": len(products),
#         "products": products
#     }


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

#     # ✅ IMAGE UPDATE SUPPORT
#     images: List[UploadFile] = File(default=[]),
#     related_images: List[UploadFile] = File(default=[]),
#     existing_image_ids: List[str] = Form(default=[]),
#     existing_related_image_ids: List[str] = Form(default=[]),

#     session: AsyncSession = Depends(get_session),
# ):

#     # -----------------------------
#     # Parse variants JSON
#     # -----------------------------
#     try:
#         variants_data = json.loads(variants)
#     except Exception:
#         raise HTTPException(status_code=400, detail="Variants must be valid JSON")

#     # -----------------------------
#     # Fetch existing product
#     # -----------------------------
#     existing_product = await get_product_by_id(product_id, session)
#     if not existing_product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     existing_images_all = json.loads(existing_product.get("images", "[]"))
#     existing_related_all = json.loads(existing_product.get("related_images", "[]"))

#     # -----------------------------
#     # Keep selected existing images
#     # -----------------------------
#     existing_images_to_keep = [
#         img for img in existing_images_all
#         if img["id"] in existing_image_ids
#     ]

#     existing_related_to_keep = [
#         img for img in existing_related_all
#         if img["id"] in existing_related_image_ids
#     ]

#     # -----------------------------
#     # Process new uploads
#     # -----------------------------
#     new_images = [
#         {
#             "id": str(uuid.uuid4()),
#             "url": save_upload(file),
#             "is_default": False
#         }
#         for file in images
#     ]

#     new_related = [
#         {
#             "id": str(uuid.uuid4()),
#             "url": save_upload(file)
#         }
#         for file in related_images
#     ]

#     final_images = existing_images_to_keep + new_images
#     final_related = existing_related_to_keep + new_related

#     # -----------------------------
#     # Build data object
#     # -----------------------------
#     product_data = {
#         "product_id": product_id,
#         "category_id": category_id,
#         "subcategory_id": subcategory_id,
#         "name": name,
#         "description": description,
#         "min_order_qty": min_order_qty,
#         "max_order_qty": max_order_qty,
#         "images": final_images,
#         "related_images": final_related,
#         "variants": variants_data,
#     }

#     result = await update_productsetup(product_id, product_data, session)

#     return {"status": "success", "product_id": result["product_id"]}


# async def update_productsetup(product_id: str, data: dict, session: AsyncSession):

#     try:
#         # -----------------------------
#         # Update Product
#         # -----------------------------
#         await session.execute(
#             text(queries["product"]["update"]),
#             {
#                 "id": product_id,
#                 "category_id": data["category_id"],
#                 "subcategory_id": data["subcategory_id"],
#                 "name": data["name"],
#                 "description": data["description"],
#                 "min_order_qty": data["min_order_qty"],
#                 "max_order_qty": data["max_order_qty"],
#                 "images": json.dumps(data["images"]),
#                 "related_images": json.dumps(data["related_images"]),
#                 "updated_at": datetime.utcnow(),
#             }
#         )

#         # -----------------------------
#         # Update Variants
#         # -----------------------------
#         for variant in data["variants"]:

#             if not variant.get("id"):
#                 raise HTTPException(status_code=400, detail="Variant ID required")

#             await session.execute(
#                 text(queries["product_variant"]["update"]),
#                 {
#                     "id": variant["id"],
#                     "product_id": product_id,
#                     "size_id": variant.get("size_id"),
#                     "paper_type_id": variant.get("paper_type_id"),
#                     "print_type_id": variant.get("print_type_id"),
#                     "cut_type_id": variant.get("cut_type_id"),
#                     "sides": variant.get("sides"),
#                     "two_side_cut": variant.get("two_side_cut"),
#                     "four_side_cut": variant.get("four_side_cut"),
#                     "orientation": variant.get("orientation"),
#                     "updated_at": datetime.utcnow(),
#                 }
#             )

#             # -----------------------------
#             # Update Prices
#             # -----------------------------
#             for price in variant.get("prices", []):

#                 if not price.get("id"):
#                     raise HTTPException(status_code=400, detail="Price ID required")

#                 discount_id = None

#                 # -----------------------------
#                 # Update Discount
#                 # -----------------------------
#                 if price.get("discount"):
#                     discount = price["discount"]

#                     if not discount.get("id"):
#                         raise HTTPException(status_code=400, detail="Discount ID required")

#                     discount_id = discount["id"]

#                     await session.execute(
#                         text(queries["product_discount"]["update"]),
#                         {
#                             "id": discount_id,
#                             "product_id": product_id,
#                             "description": discount.get("description"),
#                             "discount": discount.get("discount"),
#                             "start_date": discount.get("start_date"),
#                             "end_date": discount.get("end_date"),
#                             "updated_at": datetime.utcnow(),
#                         }
#                     )

#                 # -----------------------------
#                 # Update Price
#                 # -----------------------------
#                 await session.execute(
#                     text(queries["product_variant_price"]["update"]),
#                     {
#                         "id": price["id"],
#                         "variant_id": variant["id"],
#                         "discount_id": discount_id,
#                         "min_qty": price.get("min_qty"),
#                         "price": price.get("price"),
#                         "is_active": price.get("is_active"),
#                         "updated_at": datetime.utcnow(),
#                     }
#                 )

#         #  COMMIT ONCE AT END
#         await session.commit()

#         return {"status": "success", "product_id": product_id}

#     except Exception as e:
#         #  ROLLBACK ON ERROR
#         await session.rollback()
#         raise e

from datetime import datetime
import json
import shutil
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import text

from app.core.database import execute, query, query_all
from app.domain.productsetup_domain import ProductSetup
from app.utils.query_loader import load_queries
from app.services.productsetup_service import (
    get_product_by_id,
    get_all_products_with_details,
    create_productsetup,
    update_productsetup
)

import os
import uuid

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
                data["is_default"] = index == 0

            results.append(data)

    return results


# ---------------------------------------------------
# Core creation logic
# ---------------------------------------------------



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
):
    try:
        variants_data = json.loads(variants)
    except Exception:
        raise HTTPException(status_code=400, detail="Variants must be valid JSON")

    saved_images = process_files(images, include_default=True)
    saved_related_images = process_files(related_images)

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

    result = await create_productsetup(product)

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
async def get_product(product_id: str):
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"status": "success", "product": product}


@router.get("/list")
async def get_all_products():
    products = await get_all_products_with_details()

    return {
        "status": "success",
        "count": len(products),
        "products": products
    }


# ---------------------------------------------------
# UPDATE
# ---------------------------------------------------

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
    images: List[UploadFile] = File(default=[]),
    related_images: List[UploadFile] = File(default=[]),
    existing_image_ids: List[str] = Form(default=[]),
    existing_related_image_ids: List[str] = Form(default=[]),
):

    try:
        variants_data = json.loads(variants)
    except Exception:
        raise HTTPException(status_code=400, detail="Variants must be valid JSON")

    existing_product = await get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_images_all = json.loads(existing_product.get("images", "[]"))
    existing_related_all = json.loads(existing_product.get("related_images", "[]"))

    existing_images_to_keep = [
        img for img in existing_images_all
        if img["id"] in existing_image_ids
    ]

    existing_related_to_keep = [
        img for img in existing_related_all
        if img["id"] in existing_related_image_ids
    ]

    new_images = [
        {"id": str(uuid.uuid4()), "url": save_upload(file), "is_default": False}
        for file in images
    ]

    new_related = [
        {"id": str(uuid.uuid4()), "url": save_upload(file)}
        for file in related_images
    ]

    final_images = existing_images_to_keep + new_images
    final_related = existing_related_to_keep + new_related

    product_data = {
        "product_id": product_id,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "name": name,
        "description": description,
        "min_order_qty": min_order_qty,
        "max_order_qty": max_order_qty,
        "images": final_images,
        "related_images": final_related,
        "variants": variants_data,
    }

    result = await update_productsetup(product_id, product_data)

    return {"status": "success", "product_id": result["product_id"]}



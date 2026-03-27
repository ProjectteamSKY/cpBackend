# ROUTES FILE (Complete)
from datetime import datetime
import json
import shutil
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import text

from app.domain.productsetup_domain import ProductSetup
from app.utils.query_loader import load_queries
from app.services.productsetup_service import (
    get_product_by_id,
    get_all_products_with_details,
    create_productsetup,
    update_productsetup,
    soft_delete_product_setup_service,
    delete_productsetup
)

from app.utils.sku_generator import generate_sku


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

    # ✅ FIXED: Generate SKU from name using service function
    sku = await generate_sku(name)

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
        sku=sku,  # ✅ Pass generated SKU
    )

    result = await create_productsetup(product)

    return {
        "status": "success",
        "product_id": result["product_id"],
        "sku": sku,
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

    # ✅ FIXED: Regenerate SKU from updated name OR preserve existing
    existing_sku = existing_product.get("sku")
    new_sku = await generate_sku(name)
    sku = existing_sku if existing_sku else new_sku

    product_data = {
        "product_id": product_id,
        "sku": sku,  # ✅ Use generated/preserved SKU
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


@router.delete("/remove/{id}")
async def soft_delete_product_setup_route(id: str, type: str):
    print("a - productsetup_routes.py:223")
    result = await soft_delete_product_setup_service(id, type)
    return result


@router.delete("/delete/{product_id}")
async def delete_product_endpoint(product_id: str):
    """
    Soft delete product with all variants, prices, and discounts.
    """
    result = await delete_productsetup(product_id)
    return result
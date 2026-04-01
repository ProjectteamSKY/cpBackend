

from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import List, Optional
import os, shutil, uuid, json

from app.domain.product_domain import Product
from app.services.product_service import (
    create_product,
    get_all_products,
    get_product_by_id,
    get_products_by_category,
    update_product,
    delete_product,
    activate_product,
    deactivate_product,
    get_all_products_active,
    get_product_list_minimal,
    get_products_by_subcategory,
    get_products_by_subcategory_minimal
)
from app.utils.sku_generator import generate_sku

router = APIRouter()

UPLOAD_FOLDER = "media/products"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path.replace("\\", "/")


# ------------------------
# CREATE
# ------------------------


@router.post("/create")
async def create_product_endpoint(
    name: str = Form(...),
    category_id: Optional[str] = Form(None),
    subcategory_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    min_order_qty: int = Form(100),
    max_order_qty: Optional[int] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    related_images: Optional[List[UploadFile]] = File(None),
):
    # 🔥 FIX: Convert empty string → None
    category_id = category_id or None
    subcategory_id = subcategory_id or None
    print("NAME: - product_routes.py:57", name)
    print("CATEGORY: - product_routes.py:58", category_id)
    print("subcategory_id: - product_routes.py:59", subcategory_id)

    # Generate SKU
    sku = await generate_sku(name)

    images_list = [
        {"id": str(uuid.uuid4()), "url": save_upload(f), "is_default": i == 0}
        for i, f in enumerate(images or [])
    ]

    related_list = [
        {"id": str(uuid.uuid4()), "url": save_upload(f)}
        for f in (related_images or [])
    ]

    product = Product(
        name=name,
        sku=sku,
        category_id=category_id,
        subcategory_id=subcategory_id,
        description=description,
        min_order_qty=min_order_qty,
        max_order_qty=max_order_qty,
        images=images_list,
        related_images=related_list
    )

    return await create_product(product)


# ------------------------
# LIST / ACTIVE LIST
# ------------------------
@router.get("/list")
async def list_products():
    return {"products": await get_all_products()}

@router.get("/active/list")
async def list_active_products():
    return {"products": await get_all_products_active()}


# ------------------------
# GET BY ID
# ------------------------
@router.get("/{id}")
async def get_product_endpoint(id: str):
    product = await get_product_by_id(id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


# ------------------------
# GET BY CATEGORY
# ------------------------
@router.get("/category/{category_id}")
async def list_products_by_category(category_id: str):
    return {"products": await get_products_by_category(category_id)}


# ------------------------
# UPDATE
# ------------------------
@router.put("/{id}")
async def update_product_endpoint(
    id: str,
    name: str = Form(...),
    sku: str = Form(""),  #  Added SKU as optional form field
    category_id: Optional[str] = Form(None),
    subcategory_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    min_order_qty: int = Form(100),
    max_order_qty: Optional[int] = Form(None),
    images: List[UploadFile] = File(default=[]),
    related_images: List[UploadFile] = File(default=[]),
    existing_image_ids: List[str] = Form(default_factory=list),
    existing_related_image_ids: List[str] = Form(default_factory=list),
):
    existing_product = await get_product_by_id(id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # ✅ Use existing SKU if not provided
    update_sku = sku or existing_product.get("sku", "")

    # Handle images (unchanged)
    existing_images_all = (
        json.loads(existing_product.get("images", "[]")) 
        if isinstance(existing_product.get("images"), str) 
        else existing_product.get("images", [])
    ) or []
    
    existing_related_all = (
        json.loads(existing_product.get("related_images", "[]")) 
        if isinstance(existing_product.get("related_images"), str) 
        else existing_product.get("related_images", [])
    ) or []

    existing_images_to_keep = [
        img for img in existing_images_all 
        if img.get("id") in existing_image_ids
    ]
    existing_related_to_keep = [
        img for img in existing_related_all 
        if img.get("id") in existing_related_image_ids
    ]

    new_images = [
        {"id": str(uuid.uuid4()), "url": save_upload(f), "is_default": False} 
        for f in images
    ]
    new_related = [
        {"id": str(uuid.uuid4()), "url": save_upload(f)} 
        for f in related_images
    ]

    images_list = existing_images_to_keep + new_images
    related_list = existing_related_to_keep + new_related

    # ✅ Fixed Product creation with SKU
    product = Product(
        name=name,
        sku=update_sku,  # ✅ Now properly set
        category_id=category_id,
        subcategory_id=subcategory_id,
        description=description,
        min_order_qty=min_order_qty,
        max_order_qty=max_order_qty,
        images=images_list,
        related_images=related_list
    )

    updated = await update_product(id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return updated




# ------------------------
# DELETE / ACTIVATE / DEACTIVATE
# ------------------------
@router.delete("/{id}")
async def delete_product_endpoint(id: str):
    return await delete_product(id)

@router.put("/{id}/activate")
async def activate_product_endpoint(id: str):
    return await activate_product(id)

@router.put("/{id}/deactivate")
async def deactivate_product_endpoint(id: str):
    return await deactivate_product(id)

@router.get("/minimal/list")
async def minimal_product_list():
    products = await get_product_list_minimal()
    return {"products": products}


@router.get("/subcategory/{subcategory_id}")
async def list_products_by_subcategory(subcategory_id: str):
    return {"products": await get_products_by_subcategory(subcategory_id)}

@router.get("/subcategory/{subcategory_id}/minimal")
async def minimal_products_by_subcategory(subcategory_id: str):
    products = await get_products_by_subcategory_minimal(subcategory_id)
    return {"products": products}
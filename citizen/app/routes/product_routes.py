from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os, shutil, uuid, json

from app.core.database import get_session
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
    get_all_products_active
)

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
    session: AsyncSession = Depends(get_session)
):
    images_list = [{"id": str(uuid.uuid4()), "url": save_upload(f), "is_default": i==0} 
                   for i, f in enumerate(images or [])]
    related_list = [{"id": str(uuid.uuid4()), "url": save_upload(f)} 
                    for f in related_images or []]

    product = Product(
        name=name,
        category_id=category_id,
        subcategory_id=subcategory_id,
        description=description,
        min_order_qty=min_order_qty,
        max_order_qty=max_order_qty,
        images=images_list,
        related_images=related_list
    )

    return await create_product(product, session)


@router.get("/list")
async def list_products(session: AsyncSession = Depends(get_session)):
    return {"products": await get_all_products(session)}

@router.get("/active/list") 
async def list_products(session: AsyncSession = Depends(get_session)):
    return {"products": await get_all_products_active(session)}

@router.get("/{id}")
async def get_product_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    product = await get_product_by_id(id, session)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.get("/category/{category_id}")
async def list_products_by_category(category_id: str, session: AsyncSession = Depends(get_session)):
    return {"products": await get_products_by_category(category_id, session)}



@router.put("/{id}")
async def update_product_endpoint(
    id: str,
    name: str = Form(...),
    category_id: Optional[str] = Form(None),
    subcategory_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    min_order_qty: int = Form(100),
    max_order_qty: Optional[int] = Form(None),

    # ✅ FIXED TYPES
    images: List[UploadFile] = File(default=[]),
    related_images: List[UploadFile] = File(default=[]),
    existing_image_ids: List[str] = Form(default=[]),
    existing_related_image_ids: List[str] = Form(default=[]),

    session: AsyncSession = Depends(get_session)
):

    print("images:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ - product_routes.py:106", images)
    print("related_images:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ - product_routes.py:107", related_images)
    print("existing_image_ids:@@@@@@@@@@@@@@@@@@@@@@@@@@@@ - product_routes.py:108", existing_image_ids)
    print("existing_related_image_ids: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@ - product_routes.py:109", existing_related_image_ids)

    # Fetch existing product
    existing_product = await get_product_by_id(id, session)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Parse stored JSON
    existing_images_all = json.loads(existing_product.get("images", "[]"))
    existing_related_all = json.loads(existing_product.get("related_images", "[]"))
  
    # Keep only selected existing images
    existing_images_to_keep = [
        img for img in existing_images_all
        if img["id"] in existing_image_ids
    ]

    existing_related_to_keep = [
        img for img in existing_related_all
        if img["id"] in existing_related_image_ids
    ]

    # Process new uploads
    new_images = [
        {
            "id": str(uuid.uuid4()),
            "url": save_upload(file),
            "is_default": False
        }
        for file in images
    ]

    new_related = [
        {
            "id": str(uuid.uuid4()),
            "url": save_upload(file)
        }
        for file in related_images
    ]

    # Merge
    images_list = existing_images_to_keep + new_images
    related_list = existing_related_to_keep + new_related

    # Build product model
    product = Product(
        name=name,
        category_id=category_id,
        subcategory_id=subcategory_id,
        description=description,
        min_order_qty=min_order_qty,
        max_order_qty=max_order_qty,
        images=images_list,
        related_images=related_list
    )

    updated = await update_product(id, product, session)

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    return updated

@router.delete("/{id}")
async def delete_product_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await delete_product(id, session)


@router.put("/{id}/activate")
async def activate_product_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await activate_product(id, session)

@router.put("/{id}/deactivate")
async def activate_product_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await deactivate_product(id, session)
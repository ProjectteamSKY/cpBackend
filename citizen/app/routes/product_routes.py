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
    activate_product
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


@router.post("/product/create")
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


@router.get("/products/list")
async def list_products(session: AsyncSession = Depends(get_session)):
    return {"products": await get_all_products(session)}


@router.get("/product/{id}")
async def get_product_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    product = await get_product_by_id(id, session)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.get("/products/category/{category_id}")
async def list_products_by_category(category_id: str, session: AsyncSession = Depends(get_session)):
    return {"products": await get_products_by_category(category_id, session)}


@router.put("/product/{id}")
async def update_product_endpoint(
    id: str,
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

    updated = await update_product(id, product, session)
    if not updated:
        raise HTTPException(404, "Product not found")
    return updated


@router.delete("/product/{id}")
async def delete_product_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await delete_product(id, session)


@router.put("/product/{id}/activate")
async def activate_product_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await activate_product(id, session)
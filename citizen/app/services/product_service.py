# app/services/product_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domain.product_domain import Product as ProductDomain
from app.repository.product_repository import (
    create_product_repo,
    get_product_by_id_repo,
    get_all_products_repo,
    update_product_repo,
    delete_product_repo
)
from app.schemas.product_schema import ProductCreateSchema, ProductUpdateSchema
from app.services.product_image_service import get_all_images_by_product_service

# CREATE
async def create_product(data: ProductCreateSchema, session: AsyncSession):
    product = ProductDomain(
        name=data.name,
        category_id=data.category_id,
        subcategory_id=data.subcategory_id,
        product_type_id=data.product_type_id,
        description=data.description,
        min_order_qty=data.min_order_qty or 100,
        max_order_qty=data.max_order_qty
    )
    return await create_product_repo(product, session)

# GET ONE
async def get_product(product_id: str, session: AsyncSession):
    product = await get_product_by_id_repo(product_id, session)
    if not product:
        raise HTTPException(404, "Product not found")

    # attach images
    images = await get_all_images_by_product_service(product.id, session)
    product_dict = product.__dict__
    product_dict["images"] = [
        {"id": img.id, "image_url": img.image_url, "is_default": img.is_default} 
        for img in images
    ]
    return product_dict

# GET ALL
async def get_all_products(session: AsyncSession):
    return await get_all_products_repo(session)

# GET ALL WITH IMAGES
async def get_all_products_with_images(session: AsyncSession):
    products = await get_all_products_repo(session)
    results = []

    for product in products:
        images = await get_all_images_by_product_service(product.id, session)
        results.append({
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "subcategory_id": product.subcategory_id,
            "product_type_id": product.product_type_id,
            "description": product.description,
            "min_order_qty": product.min_order_qty,
            "max_order_qty": product.max_order_qty,
            "is_active": product.is_active,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "images": [
                {"id": img.id, "image_url": img.image_url, "is_default": img.is_default}
                for img in images
            ]
        })

    return results

# UPDATE
async def update_product(product_id: str, data: ProductUpdateSchema, session: AsyncSession):
    updated = await update_product_repo(product_id, data.model_dump(exclude_unset=True), session)
    if not updated:
        raise HTTPException(404, "Product not found")
    return updated

# DELETE
async def delete_product(product_id: str, session: AsyncSession):
    success = await delete_product_repo(product_id, session)
    if not success:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted successfully"}


# GET ALL PRODUCTS WITH IMAGES
async def get_all_products_with_images(session: AsyncSession):
    products = await get_all_products_repo(session)
    results = []

    for product in products:
        images = await get_all_images_by_product_service(product.id, session)
        results.append({
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "subcategory_id": product.subcategory_id,
            "product_type_id": product.product_type_id,
            "description": product.description,
            "min_order_qty": product.min_order_qty,
            "max_order_qty": product.max_order_qty,
            "is_active": product.is_active,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "images": [
                {"id": img.id, "image_url": img.image_url, "is_default": img.is_default}
                for img in images
            ]
        })

    return results

# app/routes/product_image_routes.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.product_image_service import (
    create_product_image_service,
    get_product_image_service,
    get_all_images_by_product_service,
    update_product_image_service,
    delete_product_image_service
)
from app.schemas.product_image_schema import ProductImageCreateSchema
import os

router = APIRouter()    

UPLOAD_FOLDER = "media/products"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CREATE
@router.post("/")
async def create_route(
    product_id: str,
    is_default: bool = False,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    data = ProductImageCreateSchema(product_id=product_id, is_default=is_default)
    return await create_product_image_service(data, file_path, session, UPLOAD_FOLDER)

# GET ONE
@router.get("/{image_id}")
async def get_route(image_id: str, session: AsyncSession = Depends(get_session)):
    return await get_product_image_service(image_id, session)

# GET ALL FOR PRODUCT
@router.get("/product/{product_id}")
async def get_all_route(product_id: str, session: AsyncSession = Depends(get_session)):
    return await get_all_images_by_product_service(product_id, session)

# UPDATE
@router.put("/{image_id}")
async def update_route(image_id: str, data: dict, session: AsyncSession = Depends(get_session)):
    return await update_product_image_service(image_id, data, session)

# DELETE
@router.delete("/{image_id}")
async def delete_route(image_id: str, session: AsyncSession = Depends(get_session)):
    return await delete_product_image_service(image_id, session)



# app/routes/product_related_image_routes.py
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.product_related_image_service import (
    create_image_service,
    create_bulk_images_service,
    get_image_service,
    get_all_images_service,
    update_image_service,
    delete_image_service
)
from app.domain.product_related_image_domain import ProductRelatedImageDomain
import os

router = APIRouter()
UPLOAD_FOLDER = "media/products"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CREATE SINGLE
@router.post("/")
async def create_route(product_id: str, file: UploadFile = File(...), is_default: bool = False, session: AsyncSession = Depends(get_session)):
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    image = ProductRelatedImageDomain(product_id=product_id, image_url=path, is_default=is_default)
    return await create_image_service(image, session, UPLOAD_FOLDER)

# CREATE MULTIPLE
@router.post("/bulk/")
async def create_bulk_route(product_id: str, files: list[UploadFile] = File(...), session: AsyncSession = Depends(get_session)):
    paths = []
    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        paths.append(path)
    return await create_bulk_images_service(product_id, paths, session, UPLOAD_FOLDER)

# GET ONE
@router.get("/{image_id}")
async def get_route(image_id: str, session: AsyncSession = Depends(get_session)):
    return await get_image_service(image_id, session)

# GET ALL FOR PRODUCT
@router.get("/product/{product_id}")
async def get_all_route(product_id: str, session: AsyncSession = Depends(get_session)):
    return await get_all_images_service(product_id, session)

# UPDATE
@router.put("/{image_id}")
async def update_route(image_id: str, data: dict, session: AsyncSession = Depends(get_session)):
    return await update_image_service(image_id, data, session)

# DELETE
@router.delete("/{image_id}")
async def delete_route(image_id: str, session: AsyncSession = Depends(get_session)):
    return await delete_image_service(image_id, session)
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.product_variant_domain import ProductVariant
from app.repository.product_variant_repository import *
from app.schemas.product_variant_schema import ProductVariantCreateSchema, ProductVariantUpdateSchema

# CREATE
async def create_product_variant(data: ProductVariantCreateSchema, session: AsyncSession) -> ProductVariant:
    variant = ProductVariant(
        product_id=data.product_id,
        paper_type_id=data.paper_type_id,
        finish_id=data.finish_id,
        cut_type_id=data.cut_type_id,
        shape_id=data.shape_id,
        size_id=data.size_id,
        sides=data.sides,
        two_side_cut=data.two_side_cut or False,
        four_side_cut=data.four_side_cut or False,
        orientation=data.orientation or "Portrait"
    )
    return await create_product_variant_repo(variant, session)

# GET ONE
async def get_product_variant(variant_id: str, session: AsyncSession) -> ProductVariant:
    variant = await get_product_variant_by_id_repo(variant_id, session)
    if not variant:
        raise HTTPException(status_code=404, detail="ProductVariant not found")
    return variant

# GET ALL
async def get_all_product_variants(session: AsyncSession) -> list[ProductVariant]:
    return await get_all_product_variants_repo(session)

# UPDATE
async def update_product_variant(variant_id: str, data: ProductVariantUpdateSchema, session: AsyncSession) -> ProductVariant:
    updated = await update_product_variant_repo(variant_id, data.model_dump(exclude_unset=True), session)
    if not updated:
        raise HTTPException(status_code=404, detail="ProductVariant not found")
    return updated

# DELETE
async def delete_product_variant(variant_id: str, session: AsyncSession):
    success = await delete_product_variant_repo(variant_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="ProductVariant not found")
    return {"message": "ProductVariant deleted successfully"}

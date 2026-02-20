from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_session
from app.domain.product_variant_domain import ProductVariant
from app.services.product_variant_service import (
    create_product_variant,
    get_all_product_variants,
    get_product_variant_by_id,
    get_product_variants_by_product,
    update_product_variant,
    delete_product_variant,
    activate_product_variant
)

router = APIRouter()


@router.post("/product_variant/create")
async def create_product_variant_endpoint(
    product_id: str = Form(...),
    size_id: str = Form(...),
    paper_type_id: Optional[str] = Form(None),
    print_type_id: Optional[str] = Form(None),
    cut_type_id: Optional[str] = Form(None),
    sides: Optional[int] = Form(None),
    two_side_cut: bool = Form(False),
    four_side_cut: bool = Form(False),
    orientation: str = Form("Portrait"),
    session: AsyncSession = Depends(get_session)
):
    variant = ProductVariant(
        product_id=product_id,
        size_id=size_id,
        paper_type_id=paper_type_id,
        print_type_id=print_type_id,
        cut_type_id=cut_type_id,
        sides=sides,
        two_side_cut=two_side_cut,
        four_side_cut=four_side_cut,
        orientation=orientation
    )
    return await create_product_variant(variant, session)


@router.get("/product_variants/list")
async def list_product_variants(session: AsyncSession = Depends(get_session)):
    return {"variants": await get_all_product_variants(session)}


@router.get("/product_variant/{id}")
async def get_product_variant_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    variant = await get_product_variant_by_id(id, session)
    if not variant:
        raise HTTPException(404, "Product Variant not found")
    return variant


@router.get("/product_variants/product/{product_id}")
async def list_product_variants_by_product(product_id: str, session: AsyncSession = Depends(get_session)):
    return {"variants": await get_product_variants_by_product(product_id, session)}


@router.put("/product_variant/{id}")
async def update_product_variant_endpoint(
    id: str,
    product_id: str = Form(...),
    size_id: str = Form(...),
    paper_type_id: Optional[str] = Form(None),
    print_type_id: Optional[str] = Form(None),
    cut_type_id: Optional[str] = Form(None),
    sides: Optional[int] = Form(None),
    two_side_cut: bool = Form(False),
    four_side_cut: bool = Form(False),
    orientation: str = Form("Portrait"),
    session: AsyncSession = Depends(get_session)
):
    variant = ProductVariant(
        product_id=product_id,
        size_id=size_id,
        paper_type_id=paper_type_id,
        print_type_id=print_type_id,
        cut_type_id=cut_type_id,
        sides=sides,
        two_side_cut=two_side_cut,
        four_side_cut=four_side_cut,
        orientation=orientation
    )
    updated = await update_product_variant(id, variant, session)
    if not updated:
        raise HTTPException(404, "Product Variant not found")
    return updated


@router.delete("/product_variant/{id}")
async def delete_product_variant_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await delete_product_variant(id, session)


@router.put("/product_variant/{id}/activate")
async def activate_product_variant_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await activate_product_variant(id, session)
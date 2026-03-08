from fastapi import APIRouter, Form, HTTPException
from typing import Optional

from app.domain.product_variant_domain import ProductVariant
from app.services.product_variant_service import (
    create_product_variant,
    get_all_product_variants,
    get_product_variant_by_id,
    get_product_variants_by_product,
    update_product_variant,
    delete_product_variant,
    activate_product_variant,
    calculate_variant_weight
)

router = APIRouter()


@router.post("/create")
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

    return await create_product_variant(variant)


@router.get("/list")
async def list_product_variants():
    return {"variants": await get_all_product_variants()}


@router.get("/{id}")
async def get_product_variant_endpoint(id: str):
    variant = await get_product_variant_by_id(id)
    if not variant:
        raise HTTPException(404, "Product Variant not found")
    return variant


@router.get("/product/{product_id}")
async def list_product_variants_by_product(product_id: str):
    return {"variants": await get_product_variants_by_product(product_id)}


@router.put("/{id}")
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

    updated = await update_product_variant(id, variant)

    if not updated:
        raise HTTPException(404, "Product Variant not found")

    return updated


@router.delete("/{id}")
async def delete_product_variant_endpoint(id: str):
    return await delete_product_variant(id)


@router.put("/{id}/activate")
async def activate_product_variant_endpoint(id: str):
    return await activate_product_variant(id)


from fastapi import Query

@router.get("/{variant_id}/weight")
async def get_variant_weight(variant_id: str, quantity: int = Query(1, gt=0)):
    """
    Calculate total weight (grams) for a product variant given a quantity.
    """

    total_weight = await calculate_variant_weight(variant_id, quantity)
    
    if total_weight is None:
        raise HTTPException(404, "Product Variant not found")
    
    return {
        "variant_id": variant_id,
        "quantity": quantity,
        "total_weight_grams": total_weight
    }
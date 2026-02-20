from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.productsetup_domain import ProductSetup
from app.services.productsetup_service import create_productsetup ,get_product_by_id

router = APIRouter(prefix="/productsetup", tags=["Product Setup"])

@router.post("/")
async def setup_product(product_data: ProductSetup, session: AsyncSession = Depends(get_session)):
    result = await create_productsetup(product_data, session)
    return result


@router.get("/products/{product_id}")
async def get_product(product_id: str, session: AsyncSession = Depends(get_session)):
    """
    Get product details including variants, prices, and discounts
    """
    product = await get_product_by_id(product_id, session)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"status": "success", "product": product}
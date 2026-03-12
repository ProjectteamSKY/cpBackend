from fastapi import APIRouter, Query
from app.services.bank_services.vpa_service import create_vpa

router = APIRouter()

@router.post("/vpa/create")
async def vpa_creation(accesstoken: str = Query(..., description="OAuth access token")):
    """
    Create a VPA by manually passing the OAuth access token.
    """
    result = await create_vpa(access_token=accesstoken)
    return result
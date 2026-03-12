from fastapi import APIRouter
from app.services.bank_services.vpa_service import create_vpa

router = APIRouter()

@router.post("/vpa/create")
async def vpa_creation():

    result = await create_vpa()

    return result
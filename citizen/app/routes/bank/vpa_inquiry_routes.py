from fastapi import APIRouter, Query
from app.services.bank_services.vpa_service import vpa_inquiry

router = APIRouter()

@router.post("/vpa-inquiry")
async def vpa_inquiry_api(
    access_token: str = Query(...),
    batch_id: str = Query(...)
):
    return await vpa_inquiry(
        access_token=access_token,
        batch_id=batch_id
    )
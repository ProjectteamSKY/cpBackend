from fastapi import APIRouter
from app.services.bank_services.vpa_inquiry_service import vpa_inquiry

router = APIRouter()

@router.post("/vpa-inquiry")
async def vpa_inquiry_api(
    mid: str,
    terminalId: str,
    sid: str,
    batch_id: str
):
    return await vpa_inquiry(mid, terminalId, sid, batch_id)
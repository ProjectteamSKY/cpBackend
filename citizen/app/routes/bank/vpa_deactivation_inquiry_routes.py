from fastapi import APIRouter
from app.services.bank_services.vpa_deactivation_inquiry_service import vpa_deactivation_inquiry

router = APIRouter()

@router.post("/vpa-deactivation-inquiry")
async def vpa_deactivation_inquiry_api(
    mid: str,
    terminalId: str,
    sid: str,
    batch_id: str
):
    return await vpa_deactivation_inquiry(mid, terminalId, sid, batch_id)
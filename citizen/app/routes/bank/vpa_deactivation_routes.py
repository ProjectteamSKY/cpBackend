from fastapi import APIRouter
from app.services.bank_services.vpa_deactivation_service import vpa_deactivation

router = APIRouter()

@router.post("/vpa-deactivate")
async def deactivate_vpa(
    mid: str,
    terminalId: str,
    sid: str,
    upiId: str
):
    return await vpa_deactivation(mid, terminalId, sid, upiId)
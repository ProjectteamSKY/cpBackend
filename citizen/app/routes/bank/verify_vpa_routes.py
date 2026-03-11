from fastapi import APIRouter
from app.services.bank_services.verify_vpa_service import verify_vpa

router = APIRouter()

@router.post("/verify-vpa")
async def verify_vpa_api(
    source: str,
    channel: str,
    extTransactionId: str,
    upiId: str,
    terminalId: str,
    sid: str
):
    return await verify_vpa(source, channel, extTransactionId, upiId, terminalId, sid)
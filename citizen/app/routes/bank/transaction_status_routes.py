from fastapi import APIRouter
from app.services.bank_services.transaction_status_service import transaction_status_rrn

router = APIRouter()

@router.post("/transaction-status-rrn")
async def transaction_status_rrn_api(
    rrn: str,
    terminalId: str,
    mid: str,
    sid: str
):
    return await transaction_status_rrn(rrn, terminalId, mid, sid)
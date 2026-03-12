from fastapi import APIRouter
from app.services.bank_services.transaction_status_extid_service import transaction_status_extid

router = APIRouter()

@router.post("/transaction-status-extid")
async def transaction_status_extid_api(
    mid: str,
    terminalId: str,
    sid: str,
    extTransactionId: str
):
    return await transaction_status_extid(mid, terminalId, sid, extTransactionId)
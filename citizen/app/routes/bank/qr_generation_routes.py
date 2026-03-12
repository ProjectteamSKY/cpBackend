from fastapi import APIRouter
from app.services.bank_services.qr_generation_service import generate_qr

router = APIRouter()

@router.post("/qr-generate")
async def qr_generate_api(
    amount: str,
    extTransactionId: str,
    remark: str,
    source: str,
    terminalId: str,
    sid: str,
    upiId: str,
    requestTime: str,
    receipt: str
):
    return await generate_qr(
        amount,
        extTransactionId,
        remark,
        source,
        terminalId,
        sid,
        upiId,
        requestTime,
        receipt
    )
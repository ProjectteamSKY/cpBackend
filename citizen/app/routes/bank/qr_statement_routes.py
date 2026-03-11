from fastapi import APIRouter
from app.services.bank_services.qr_statement_service import get_qr_statement

router = APIRouter()

@router.post("/qr-statement")
async def qr_statement(
    mid: str,
    sid: str,
    terminalId: str,
    startDate: str,
    endDate: str,
    pageSize: str = "10",
    pageNo: str = "1"
):
    return await get_qr_statement(
        mid,
        sid,
        terminalId,
        startDate,
        endDate,
        pageSize,
        pageNo
    )   
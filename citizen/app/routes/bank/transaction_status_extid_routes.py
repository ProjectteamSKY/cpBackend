from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.bank_services.vpa_service import get_qr_status_extid

router = APIRouter()
class QRStatusExtIdRequest(BaseModel):
    extTransactionId: str
    access_token: str
@router.post("/qr-status-extid")
async def qr_status_extid_route(payload: QRStatusExtIdRequest):
    try:
        if not payload.extTransactionId:
            raise HTTPException(status_code=400, detail="extTransactionId is required")

        if not payload.access_token:
            raise HTTPException(status_code=400, detail="Access token is required")

        response = await get_qr_status_extid(
            access_token=payload.access_token,
            ext_transaction_id=payload.extTransactionId
        )

        return {
            "success": True,
            "data": response
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"QR status (extId) failed: {str(e)}"
        )
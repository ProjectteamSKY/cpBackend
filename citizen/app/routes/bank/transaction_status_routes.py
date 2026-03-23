from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.bank_services.vpa_service import get_qr_status_rrn

router = APIRouter()
class QRStatusRequest(BaseModel):
    rrn: str
    access_token: str

    
@router.post("/qr-status-rrn")
async def qr_status_rrn_route(payload: QRStatusRequest):
    try:
        if not payload.rrn:
            raise HTTPException(status_code=400, detail="RRN is required")

        if not payload.access_token:
            raise HTTPException(status_code=400, detail="Access token is required")

        response = await get_qr_status_rrn(
            access_token=payload.access_token,
            rrn=payload.rrn
        )

        return {
            "success": True,
            "data": response
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"QR status fetch failed: {str(e)}"
        )
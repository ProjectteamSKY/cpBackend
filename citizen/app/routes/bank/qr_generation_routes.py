from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.services.bank_services.vpa_service import generate_qr ,generate_qr_image ,build_clean_upi_qr

router = APIRouter()

@router.post("/qr-generate")
async def qr_generate_api(
    access_token: str = Query(..., description="OAuth access token")
):
    return await generate_qr(access_token=access_token)

from pydantic import BaseModel

class QRRequest(BaseModel):
    upiId: str
    amount: str
    extTransactionId: str
    remark: str | None = "Payment"

@router.post("/qr-image")
async def generate_qr_from_response(data: QRRequest):
    try:
        # ✅ Extract values safely
        upi_id = data.upiId
        amount = data.amount
        txn_id = data.extTransactionId
        note = data.remark or "Payment"
        name = "Dynamicqrcode"

        # ✅ Build clean UPI string
        qr_string = build_clean_upi_qr(
            upi_id=upi_id,
            name=name,
            amount=amount,
            txn_id=txn_id,
            note=note
        )

        print("CLEAN QR STRING: - qr_generation_routes.py:40", qr_string)

        # ✅ Generate QR image
        buffer = generate_qr_image(qr_string)

        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
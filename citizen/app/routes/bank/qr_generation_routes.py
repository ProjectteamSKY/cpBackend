import base64
from typing import Dict

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.services.bank_services.vpa_service import generate_qr ,generate_qr_image ,build_clean_upi_qr

router = APIRouter()

@router.post("/qr-generate")
async def qr_generate_api(
    amount: str = Query(..., description="Payment amount"),
):
    try:
        result: Dict = await generate_qr(amount=amount)

        qr_image = result.get("qr_image")
        txn_id = result.get("transaction_id")

        if not qr_image or not txn_id:
            raise HTTPException(status_code=500, detail="QR generation failed")

        # ✅ Convert image → base64
        qr_base64 = base64.b64encode(qr_image.getvalue()).decode()

        return {
            "transaction_id": txn_id,
            "qr_image": qr_base64
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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

        print("CLEAN QR STRING: - qr_generation_routes.py:62", qr_string)

        # ✅ Generate QR image
        buffer = generate_qr_image(qr_string)

        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
import json
from app.services.bank_services.vpa_service import process_qr_callback


router = APIRouter()

@router.post("/upi-callback")   # MUST be POST
async def qr_callback(request: Request):
    try:
        body = await request.json()
        print("RAW CALLBACK: - qr_callback_routes.py:13", body)

        # 👉 process callback
        await process_qr_callback(body)

        # 👉 NPCI expects EXACT response
        return PlainTextResponse("200_OK", status_code=200)

    except Exception as e:
        print("Callback Error: - qr_callback_routes.py:22", str(e))
        raise HTTPException(status_code=400, detail=str(e))
# from fastapi import APIRouter, HTTPException, Request


# router = APIRouter()

# @router.post("/upi-callback")
# async def qr_callback(request: Request):
#     try:
#         payload = await request.json()

#         result = await process_qr_callback(payload)

#         # ✅ Always send ACK to bank
#         return {
#             "Response": result
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
import json
from app.services.bank_services.vpa_service import process_qr_callback


router = APIRouter()

@router.post("/upi-callback")   # ⚠️ MUST be POST (not GET)
async def qr_callback(request: Request):
    try:
        body = await request.json()
        print("RAW CALLBACK: - qr_callback_routes.py:34", body)

        # 👉 call service
        await process_qr_callback(body)

        # 👉 NPCI / Bank expects THIS EXACT RESPONSE
        return PlainTextResponse("200_OK", status_code=200)

    except Exception as e:
        print("Callback Error: - qr_callback_routes.py:43", str(e))
        raise HTTPException(status_code=400, detail=str(e))
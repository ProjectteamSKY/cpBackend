from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/qr-callback")
async def qr_callback(request: Request):

    payload = await request.json()

    encryptData = payload.get("Request", {}).get("body", {}).get("encryptData", {})

    extTransactionId = encryptData.get("extTransactionId")
    status = encryptData.get("status")
    amount = encryptData.get("amount")
    rrn = encryptData.get("rrn")
    customer_vpa = encryptData.get("customer_vpa")

    # Example: update order payment status in DB
    print("Transaction ID: - qr_callback_routes.py:19", extTransactionId)
    print("Status: - qr_callback_routes.py:20", status)
    print("RRN: - qr_callback_routes.py:21", rrn)
    print("Amount: - qr_callback_routes.py:22", amount)

    if status == "SUCCESS":
        # update order as PAID
        pass

    return {"Response": "200_OK"}
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# import httpx
# import qrcode
# import uuid
# import os
# import json
# import base64
# from fastapi import APIRouter, HTTPException



# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad

# router = APIRouter()

# # -----------------------------
# # CANARA CONFIGURATION
# # -----------------------------

# CLIENT_ID = ""
# CLIENT_SECRET = ""
# SYMMETRIC_KEY = ""
# MERCHANT_ID = ""

# TOKEN_URL = "https://developer.canarauat.bank.in/token"
# QR_API_URL = "https://developer.canarauat.bank.in/upi/dynamicQR"
# STATUS_API_URL = "https://developer.canarauat.bank.in/upi/transactionStatus"


# QR_FOLDER = "qrs"
# os.makedirs(QR_FOLDER, exist_ok=True)

# # -----------------------------
# # AES ENCRYPTION FUNCTION
# # -----------------------------

# def encrypt_payload(payload: dict):

#     key = SYMMETRIC_KEY.encode()

#     cipher = AES.new(key, AES.MODE_ECB)

#     payload_str = json.dumps(payload)

#     encrypted = cipher.encrypt(pad(payload_str.encode(), AES.block_size))

#     return base64.b64encode(encrypted).decode()


# # -----------------------------
# # GET ACCESS TOKEN
# # -----------------------------

# async def get_token():

#     async with httpx.AsyncClient() as client:

#         res = await client.post(
#             TOKEN_URL,
#             data={"grant_type": "client_credentials"},
#             auth=(CLIENT_ID, CLIENT_SECRET)
#         )
#         print("STATUS: - payment_routes.py:65", res)

#         print("STATUS: - payment_routes.py:67", res.status_code)
#         print("RESPONSE: - payment_routes.py:68", res.text)
#     if res.status_code != 200:
#         raise HTTPException(500, "Token generation failed")

#     return res.json()["access_token"]


# # -----------------------------
# # GENERATE PAYMENT QR
# # -----------------------------



# # ----------------------------------
# # GENERATE PAYMENT QR
# # ----------------------------------
# @router.get("/create_payment/{amount}")
# async def create_payment(amount: int):

#     try:
#         token = await get_token()

#         txn_id = f"TXN-{uuid.uuid4().hex[:8]}"

#         payload = {
#             "merchantId": MERCHANT_ID,
#             "merchantName": "CitizenPrints",
#             "txnId": txn_id,
#             "amount": str(amount),
#             "currency": "INR"
#         }

#         encrypted_payload = encrypt_payload(payload)

#         body = {"request": encrypted_payload}

#         async with httpx.AsyncClient(timeout=30) as client:

#             res = await client.post(
#                 QR_API_URL,
#                 headers={
#                     "Authorization": f"Bearer {token}",
#                     "Content-Type": "application/json",
#                     "x-api-key": CLIENT_ID
#                 },
#                 json=body
#             )

#         if res.status_code != 200:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"QR generation failed: {res.text}"
#             )

#         data = res.json()

#         # Adjust if API wraps response differently
#         qr_string = data.get("qrString")

#         if not qr_string:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"QR string missing in response: {data}"
#             )

#         path = os.path.join(QR_FOLDER, f"{txn_id}.png")

#         img = qrcode.make(qr_string)
#         img.save(path)

#         return {
#             "status": "success",
#             "transaction_id": txn_id,
#             "amount": amount,
#             "qr_image_url": f"/qr/{txn_id}"
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # ----------------------------------
# # SHOW QR IMAGE
# # ----------------------------------
# @router.get("/qr/{txn_id}")
# def show_qr(txn_id: str):

#     path = os.path.join(QR_FOLDER, f"{txn_id}.png")

#     if not os.path.exists(path):
#         raise HTTPException(status_code=404, detail="QR not found")

#     return FileResponse(path, media_type="image/png")


# # ----------------------------------
# # CHECK PAYMENT STATUS
# # ----------------------------------
# @router.get("/payment_status/{txn_id}")
# async def payment_status(txn_id: str):

#     try:
#         token = await get_token()

#         payload = {
#             "merchantId": MERCHANT_ID,
#             "txnId": txn_id
#         }

#         encrypted_payload = encrypt_payload(payload)

#         body = {"request": encrypted_payload}

#         async with httpx.AsyncClient(timeout=30) as client:

#             res = await client.post(
#                 STATUS_API_URL,
#                 headers={
#                     "Authorization": f"Bearer {token}",
#                     "Content-Type": "application/json",
#                     "x-api-key": CLIENT_ID
#                 },
#                 json=body
#             )

#         if res.status_code != 200:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Status API error: {res.text}"
#             )

#         return res.json()

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
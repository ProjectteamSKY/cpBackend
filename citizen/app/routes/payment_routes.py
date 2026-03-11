from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import httpx
import qrcode
import uuid
import os
import json
import base64
from fastapi import APIRouter, HTTPException



from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

router = APIRouter()

# -----------------------------
# CANARA CONFIGURATION
# -----------------------------

CLIENT_ID = "AUx27zglhuuiRxahKUTmpAVEVKuJ3rsr"
CLIENT_SECRET = "B7WgKfGeURXYkEgRA1ZASYRFtUG64SEn"
SYMMETRIC_KEY = "0c5b95196e8e306eff0b6a9e0d37c878806954401620f2a4a30fbd0f031697e8"
MERCHANT_ID = "RNFMID0001"

TOKEN_URL = "https://developer.canarauat.bank.in/token"
QR_API_URL = "https://developer.canarauat.bank.in/upi/dynamicQR"
STATUS_API_URL = "https://developer.canarauat.bank.in/upi/transactionStatus"


QR_FOLDER = "qrs"
os.makedirs(QR_FOLDER, exist_ok=True)

# -----------------------------
# AES ENCRYPTION FUNCTION
# -----------------------------

def encrypt_payload(payload: dict):

    key = SYMMETRIC_KEY.encode()

    cipher = AES.new(key, AES.MODE_ECB)

    payload_str = json.dumps(payload)

    encrypted = cipher.encrypt(pad(payload_str.encode(), AES.block_size))

    return base64.b64encode(encrypted).decode()


# -----------------------------
# GET ACCESS TOKEN
# -----------------------------

async def get_token():

    async with httpx.AsyncClient() as client:

        res = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        print("STATUS: - payment_routes.py:65", res)

        print("STATUS: - payment_routes.py:67", res.status_code)
        print("RESPONSE: - payment_routes.py:68", res.text)
    if res.status_code != 200:
        raise HTTPException(500, "Token generation failed")

    return res.json()["access_token"]


# -----------------------------
# GENERATE PAYMENT QR
# -----------------------------

@router.get("/create_payment/{amount}")
async def create_payment(amount: int):

    token = await get_token()

    txn_id = "TXN-" + str(uuid.uuid4())[:8]

    payload = {
        "merchantId": MERCHANT_ID,
        "merchantName": "CitizenPrints",
        "txnId": txn_id,
        "amount": str(amount),
        "currency": "INR"
    }

    encrypted_payload = encrypt_payload(payload)

    body = {
        "request": encrypted_payload
    }

    async with httpx.AsyncClient() as client:

        res = await client.post(
            QR_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "x-api-key": CLIENT_ID
            },
            json=body
        )

    if res.status_code != 200:
        raise HTTPException(500, "QR generation failed")

    data = res.json()

    qr_string = data.get("qrString")

    if not qr_string:
        raise HTTPException(500, "QR string not received")

    path = f"{QR_FOLDER}/{txn_id}.png"

    img = qrcode.make(qr_string)
    img.save(path)

    return {
        "transaction_id": txn_id,
        "amount": amount,
        "qr_image": f"/qr/{txn_id}"
    }


# -----------------------------
# SHOW QR IMAGE
# -----------------------------

@router.get("/qr/{txn_id}")
def show_qr(txn_id: str):

    path = f"{QR_FOLDER}/{txn_id}.png"

    if not os.path.exists(path):
        raise HTTPException(404, "QR not found")

    return FileResponse(path, media_type="image/png")


# -----------------------------
# CHECK PAYMENT STATUS
# -----------------------------

@router.get("/payment_status/{txn_id}")
async def payment_status(txn_id: str):

    token = await get_token()

    payload = {
        "merchantId": MERCHANT_ID,
        "txnId": txn_id
    }

    encrypted_payload = encrypt_payload(payload)

    body = {
        "request": encrypted_payload
    }

    async with httpx.AsyncClient() as client:

        res = await client.post(
            STATUS_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "x-api-key": CLIENT_ID
            },
            json=body
        )

    if res.status_code != 200:
        raise HTTPException(500, "Status API error")

    return res.json()
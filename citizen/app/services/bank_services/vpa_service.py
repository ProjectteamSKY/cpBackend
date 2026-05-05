import json
import base64
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
import os
from jwcrypto import jwe, jwk
from cryptography import x509
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from io import BytesIO
from app.domain.transaction_domain import Transaction
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all
import logging

queries = load_queries()

from app.services.bank_services.oauth_service import get_valid_access_token


API_URL = "https://api.canara.bank.in/v1/upi/vpa-creation"  #  FROM YOUR LOG
VPA_ENQUIRY_URL = "https://api.canara.bank.in/v1/upi/vpa-creation-enq"
QR_GENERATION_URL = "https://api.canara.bank.in/v1/upi/qr-generation"

CLIENT_ID = "HlpU92cKxh4Aq3wwOMttGsyKddgneAl2"
CLIENT_SECRET =  b"vh8LSH58ZuVCFSNMcAnOxf9lpGth1aNg"

# PUBLIC_KEY = "MIIDvzCCAqcCFAVhG9nlbXeEi19I2ad0MPUbYhsRMA0GCSqGSIb3DQEBCwUAMIGbMQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGFtaWxuYWR1MRAwDgYDVQQHDAdDaGVubmFpMRYwFAYDVQQKDA1DaXRpemVucHJpbnRzMQswCQYDVQQLDAJJVDEZMBcGA1UEAwwQY2l0aXplbnByaW50ei5pbjEmMCQGCSqGSIb3DQEJARYXY2l0aXplbnByaW50c0BnbWFpbC5jb20wHhcNMjYwMzEwMTE0MDIwWhcNMjcwMzEwMTE0MDIwWjCBmzELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRhbWlsbmFkdTEQMA4GA1UEBwwHQ2hlbm5haTEWMBQGA1UECgwNQ2l0aXplbnByaW50czELMAkGA1UECwwCSVQxGTAXBgNVBAMMEGNpdGl6ZW5wcmludHouaW4xJjAkBgkqhkiG9w0BCQEWF2NpdGl6ZW5wcmludHNAZ21haWwuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqppbQSbJSsvHfY1XFc52LyzfD6TOpdlkR/Gr41RNNtKQSgosMrUk249EINxfs81/NQUtCzXl3fdI1ZJXwqWVoJ/cwSnToHAGnX0WyqKnBomXl+yD4tMt2m9KYXkGIx2sKrvQiN9OTebOJGDiE/lk6jsFLGfD1v22egpK1o2Myx5JZTVhVWQgurEelLlig1TWFnk+oBrYsr4q8Ur749eoLNP1e00tqeArIStRqDAVJDr/H8K7Esng6g0XeadblIw+crx6Qcb0CuoLE4oweTDIAreZWnsc3xV3AbwFTPLSc0CwSFnt7f8g3qqV+r6GJl/kI7Gvb8vN/3HnooFtT/0oyQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCl8DuzsNM/lRm7zKBPRCScO/bj3MicSqIkN7KxDg1JxfTWBE1L2SyyxH5+eP4t1GBrZOFxZ6l167dc/HQub4SYP3eb/XvjZJJ2MEYWAWiHVf9rD6uFZdXuDvryLyDgWomz5kaULRHuhIjQqxypuMnMAjf5Gq8bIRgHSsP0TKQxeZeoXrtx9aZxrBS4gpnt41v6KqeZGnLdOJY7uNE8mDrFZnOeWDIh2chs/z5zPFLEHkK46TqXmnyKIH7S6/oSmTo0zHSPFWk0XwjhgQMqYRd4ydGesL6hnakiK41nassgOIpZWt1AysqIzH3kNhOo43LL0PA5qD/g1C4boZpW1AS4"
# PUBLIC_KEY = "MIIDvzCCAqcCFAVhG9nlbXeEi19I2ad0MPUbYhsRMA0GCSqGSIb3DQEBCwUAMIGbMQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGFtaWxuYWR1MRAwDgYDVQQHDAdDaGVubmFpMRYwFAYDVQQKDA1DaXRpemVucHJpbnRzMQswCQYDVQQLDAJJVDEZMBcGA1UEAwwQY2l0aXplbnByaW50ei5pbjEmMCQGCSqGSIb3DQEJARYXY2l0aXplbnByaW50c0BnbWFpbC5jb20wHhcNMjYwMzEwMTE0MDIwWhcNMjcwMzEwMTE0MDIwWjCBmzELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRhbWlsbmFkdTEQMA4GA1UEBwwHQ2hlbm5haTEWMBQGA1UECgwNQ2l0aXplbnByaW50czELMAkGA1UECwwCSVQxGTAXBgNVBAMMEGNpdGl6ZW5wcmludHouaW4xJjAkBgkqhkiG9w0BCQEWF2NpdGl6ZW5wcmludHNAZ21haWwuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqppbQSbJSsvHfY1XFc52LyzfD6TOpdlkR/Gr41RNNtKQSgosMrUk249EINxfs81/NQUtCzXl3fdI1ZJXwqWVoJ/cwSnToHAGnX0WyqKnBomXl+yD4tMt2m9KYXkGIx2sKrvQiN9OTebOJGDiE/lk6jsFLGfD1v22egpK1o2Myx5JZTVhVWQgurEelLlig1TWFnk+oBrYsr4q8Ur749eoLNP1e00tqeArIStRqDAVJDr/H8K7Esng6g0XeadblIw+crx6Qcb0CuoLE4oweTDIAreZWnsc3xV3AbwFTPLSc0CwSFnt7f8g3qqV+r6GJl/kI7Gvb8vN/3HnooFtT/0oyQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCl8DuzsNM/lRm7zKBPRCScO/bj3MicSqIkN7KxDg1JxfTWBE1L2SyyxH5+eP4t1GBrZOFxZ6l167dc/HQub4SYP3eb/XvjZJJ2MEYWAWiHVf9rD6uFZdXuDvryLyDgWomz5kaULRHuhIjQqxypuMnMAjf5Gq8bIRgHSsP0TKQxeZeoXrtx9aZxrBS4gpnt41v6KqeZGnLdOJY7uNE8mDrFZnOeWDIh2chs/z5zPFLEHkK46TqXmnyKIH7S6/oSmTo0zHSPFWk0XwjhgQMqYRd4ydGesL6hnakiK41nassgOIpZWt1AysqIzH3kNhOo43LL0PA5qD/g1C4boZpW1AS4"


PUBLIC_KEY = "MIIGlzCCBP+gAwIBAgIQBEu3ERYfD2xIDvzaJ8yIEjANBgkqhkiG9w0BAQsFADBgMQswCQYDVQQGEwJHQjEYMBYGA1UEChMPU2VjdGlnbyBMaW1pdGVkMTcwNQYDVQQDEy5TZWN0aWdvIFB1YmxpYyBTZXJ2ZXIgQXV0aGVudGljYXRpb24gQ0EgRFYgUjM2MB4XDTI2MDQyNDAwMDAwMFoXDTI2MTAyMzIzNTk1OVowGzEZMBcGA1UEAxMQY2l0aXplbnByaW50ei5pbjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALhx9eeuHVQhZsyPca+1glmVYfDgfYEoNgc2hNEHctGR7Z91DqtzFHsLynWhzoQXFIauMUNXf48snfnKBb8B9e75QzG9JypJp/gfEu/KbcPp/07MQxztEg1peifhvkwBuGb5x2KLqRgojwYWP+nfnj3ftHhMgJhRTqKrDVJBvbOB9URsdTUSR6sB4dw5NhMDCkZzoqC3/Bk58Q7dXF7BFXR5jikp4rVzp9MacMLqCL16sxt4Ev8jePEXI+rA/7RxeFWEfaOiuaiGJm8kOV59pESK4xRUMfdaXzcsA6TrQLwylckptyPe0qTG1UhnARckG/cj8y49tSPt5x98Fycep9MCAwEAAaOCAxAwggMMMB8GA1UdIwQYMBaAFGjAEhYYDq/O9oemMlejRlFdywcnMB0GA1UdDgQWBBSMrvgKCwE5sjlyKogKwsHq5PEcXzAOBgNVHQ8BAf8EBAMCBaAwDAYDVR0TAQH/BAIwADAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwSQYDVR0gBEIwQDA0BgsrBgEEAbIxAQICBzAlMCMGCCsGAQUFBwIBFhdodHRwczovL3NlY3RpZ28uY29tL0NQUzAIBgZngQwBAgEwgYQGCCsGAQUFBwEBBHgwdjBPBggrBgEFBQcwAoZDaHR0cDovL2NydC5zZWN0aWdvLmNvbS9TZWN0aWdvUHVibGljU2VydmVyQXV0aGVudGljYXRpb25DQURWUjM2LmNydDAjBggrBgEFBQcwAYYXaHR0cDovL29jc3Auc2VjdGlnby5jb20wMQYDVR0RBCowKIIQY2l0aXplbnByaW50ei5pboIUd3d3LmNpdGl6ZW5wcmludHouaW4wggGGBgorBgEEAdZ5AgQCBIIBdgSCAXIBcAB3ANdtfRDRp/V3wsfpX9cAv/mCyTNaZeHQswFzF8DIxWl3AAABnb8SZekAAAQDAEgwRgIhAPEFL6YS2vUcRsQRMdQ8rg/Oi/lHAVKymX3oqOXBTeTEAiEAksyjI/K+zp3bRilcX3UKM5Hmceb92atpQmM6lgtLuXMAdgDIo8R/x7OtuTVrAT9qehJt4zpOQ6XGRvmXrTl1mR3PmgAAAZ2/EmZIAAAEAwBHMEUCIB1uFD5EJ2jKseZHC77F1LZqMp2R+mdut6IMSTNYb9YfAiEA6LFrdY5B9wUKkcTEqFa3vcXcq/BffBTdk4UriQsTHygAfQBs/lAZQ6heqRa8UtEz5NzJHvFBHH0lhCDRc4CeGBjrOgAAAZ2/EmWPAAgAAAUACIXmwgQDAEYwRAIgSh3Y4M7y0W8H0Vm/QxSSQsOlhJ32wmKCQB4hcHC6LjUCIA7/sXbG1k2R+nFa1gUJeX/gjAZ3WW1zn0hTdWYlvR+7MA0GCSqGSIb3DQEBCwUAA4IBgQAWnF+nbXO7tq9MfRZiFdRZCOnZU+r8lXQCt5G5qyYsKHERkn0yHIDIs/80ZYsrDdHYWeGLKa27SOjF8ss/EqCrvpXo3jrwvNfw99MKz5M7grlW0D081zQXgkSMfNFlVNVOWSvc0Q32ycScljakrLr74yLIyFJb56ibcnt/3a/dwTlmZ8nyzgg70xgMnibONqmBOWiXT/TMXFkA8HNax4WMX6OyMvQB/CSfiF5E/gmc9kTfP6m1LnU55l7/7X16j7rC5RrZcED5cpoq6lwwqiCmoKCECpGUfR5B0jsL+buQiJj28vGr7YXifD/0IDY7qbjuZUsCJtXx0252v4RZJgotEy8QsEQp8flxh5O8cfNpPx0w4ByZZd/Y1NEEypvYwgR7J2mnWGXRwlLIQ1p4Vs86UePW1s05b7B6dSIWscMc0WQFx0MXmEBG3l+V1O5Ns40N7z9ZqTijAeApmLi85ToFhdJGvUs7VkuidzENXJttFRmqfWtTCrcnoARzn2PoiBo="
SYMMETRIC_KEY = bytes.fromhex(
    "4d7a98982739e508985fdd5a3606bee53a27b3dde8850f7f1b65a2ecda996262"
)

PRIVATE_KEY_PATH = Path(__file__).resolve().parents[3] / "private_key.pem"  # Adjust path as needed
CLIENT_IP = "103.122.53.71"


# ================= SIGN FUNCTION =================
def sign_payload(payload_str: str) -> str:
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    signature = private_key.sign(
        payload_str.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode("utf-8")


# ================= ENCRYPT FUNCTION =================
def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def encrypt_data(data: dict) -> str:
    #  MUST be 32 bytes
    if len(SYMMETRIC_KEY) != 32:
        raise ValueError(f"Invalid key length: {len(SYMMETRIC_KEY)} (must be 32)")

    # Compact JSON
    payload_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    #  Create symmetric JWK
    key = jwk.JWK(
        kty="oct",
        k=b64url(SYMMETRIC_KEY)
    )

    #  Exact header required by bank
    protected_header = {
        "alg": "A256KW",
        "enc": "A128CBC-HS256"
    }

    # Create JWE
    jwetoken = jwe.JWE(
        plaintext=payload_json.encode("utf-8"),
        protected=protected_header
    )

    jwetoken.add_recipient(key)

    token = jwetoken.serialize(compact=True)

    # 🔍 DEBUG
    parts = token.split(".")
    print("JWE PARTS COUNT: - vpa_service.py:106", len(parts))  # must be 5

    return token

def decrypt_data(jwe_token: str) -> dict:
    key = jwk.JWK(
        kty="oct",
        k=base64.urlsafe_b64encode(SYMMETRIC_KEY).decode().rstrip("=")
    )

    jwetoken = jwe.JWE()
    jwetoken.deserialize(jwe_token)

    jwetoken.decrypt(key)

    decrypted_payload = jwetoken.payload.decode("utf-8")

    print("DECRYPTED STRING: - vpa_service.py:123", decrypted_payload)

    return json.loads(decrypted_payload)
# ================= CREATE VPA ================= 
# changes made by saravana line 122
async def create_vpa(access_token: str, user_id: str) -> Dict:
    # MIDCPRIN01 MID WAS PRODUCTION 
    # 7338
    #STEP 1: RAW DATA
    request_data = {
        "mid": "MIDCPRIN01",
        "channel": "API",
        "account_number": "60441010001739",
        "mobile_number": "7094006002",
        "terminalId": "TRDCIN0001",
        "name": "CitizenprintsQrcode",
        "bank_name": "Canara Bank",
        "mcc": "7338",
        "ifsc_code": "CNRB0016044",
        "checksum": "",
        "additionalNo": " ",
        "sid": "SIDCIN0001"
    }

    #STEP 2: SIGN PAYLOAD (PLAIN)
    plain_payload = {
        "Request": {
            "body": {
                "encryptData": request_data
            }
        }
    }

    payload_str_for_sign = json.dumps(
        plain_payload,
        separators=(",", ":"),
        ensure_ascii=False
    )

    print("SIGN PAYLOAD: - vpa_service.py:162", payload_str_for_sign)

    signature = sign_payload(payload_str_for_sign)
    print("SIGNATURE: - vpa_service.py:165", signature)

    # 🔹 STEP 3: ENCRYPT ONLY request_data
    encrypted_string = encrypt_data(request_data)
    print("ENCRYPTED: - vpa_service.py:169", encrypted_string)

    # 🔹 STEP 4: FINAL PAYLOAD
    final_payload = {
        "Request": {
            "body": {
                "encryptData": encrypted_string
            }
        }
    }

    payload_str = json.dumps(final_payload, separators=(",", ":"))
    print("FINAL PAYLOAD: - vpa_service.py:181", payload_str)

    #STEP 5: HEADERS
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-client-certificate": PUBLIC_KEY.strip(),
        "x-api-interaction-id": str(uuid.uuid4()),
        "x-timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-signature": signature,
        "x-forwarded-for": CLIENT_IP,
    }

    print("HEADERS: - vpa_service.py:197", headers)

    #STEP 6: API CALL
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            API_URL,
            headers=headers,
            content=payload_str
        )

    # 🔍 DEBUG RESPONSE
    print("STATUS: - vpa_service.py:208", response.status_code)
    print("RAW RESPONSE: - vpa_service.py:209", response.text)

    try:
        resp_json = response.json()

        encrypted_resp = resp_json["Response"]["body"]["encryptData"]
        print("ENCRYPTED RESPONSE: - vpa_service.py:215", encrypted_resp)

        decrypted_resp = decrypt_data(encrypted_resp)

        print("DECRYPTED RESPONSE: - vpa_service.py:219", decrypted_resp)

        return decrypted_resp

    except Exception as e:
        print("DECRYPT ERROR: - vpa_service.py:224", str(e))
        return {
            "status": response.status_code,
            "raw": response.text
        }
    
async def vpa_inquiry(access_token: str, batch_id: str) -> Dict:

    # 🔹 STEP 1: REQUEST DATA (ONLY CHANGE FROM CREATE API)
    request_data = {
        "channel": "API",
        "mid": "MIDCPRIN01",
        "terminalId": "TRDCIN0001",
        "sid": "SIDCIN0001",
        "batch_id": batch_id,
        "checksum": ""
    }

    # 🔹 STEP 2: SIGN PAYLOAD (PLAIN JSON)
    plain_payload = {
        "Request": {
            "body": {
                "encryptData": request_data
            }
        }
    }

    payload_str_for_sign = json.dumps(
        plain_payload,
        separators=(",", ":"),
        ensure_ascii=False
    )

    print("SIGN PAYLOAD (ENQ): - vpa_service.py:257", payload_str_for_sign)

    signature = sign_payload(payload_str_for_sign)
    print("SIGNATURE (ENQ): - vpa_service.py:260", signature)

    # 🔹 STEP 3: ENCRYPT ONLY request_data
    encrypted_string = encrypt_data(request_data)
    print("ENCRYPTED (ENQ): - vpa_service.py:264", encrypted_string)

    # 🔹 STEP 4: FINAL PAYLOAD
    final_payload = {
        "Request": {
            "body": {
                "encryptData": encrypted_string
            }
        }
    }

    payload_str = json.dumps(final_payload, separators=(",", ":"))
    print("FINAL PAYLOAD (ENQ): - vpa_service.py:276", payload_str)

    # 🔹 STEP 5: HEADERS
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,  #  string only
        "x-client-certificate": PUBLIC_KEY.strip(),
        "x-api-interaction-id": str(uuid.uuid4()),
        "x-timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-signature": signature,
        "x-forwarded-for": CLIENT_IP,
    }

    print("HEADERS (ENQ): - vpa_service.py:292", headers)

    # 🔹 STEP 6: API CALL
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            VPA_ENQUIRY_URL,
            headers=headers,
            content=payload_str
        )

    print("STATUS (ENQ): - vpa_service.py:302", response.status_code)
    print("RAW RESPONSE (ENQ): - vpa_service.py:303", response.text)

    # 🔹 STEP 7: DECRYPT RESPONSE
    try:
        resp_json = response.json()

        encrypted_resp = resp_json["Response"]["body"]["encryptData"]
        print("ENCRYPTED RESPONSE (ENQ): - vpa_service.py:310", encrypted_resp)

        decrypted_resp = decrypt_data(encrypted_resp)

        print("DECRYPTED RESPONSE (ENQ): - vpa_service.py:314", decrypted_resp)

        return decrypted_resp

    except Exception as e:
        print("DECRYPT ERROR (ENQ): - vpa_service.py:319", str(e))
        return {
            "status": response.status_code,
            "raw": response.text
        }

async def generate_unique_ext_txn_id():
    while True:
        txn_id = f"EXT{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"

        existing = await query(
            """
            SELECT id 
            FROM transactions 
            WHERE ext_transaction_id = :txn_id
            """,
            {"txn_id": txn_id}
        )

        if not existing:
            return txn_id
            
#changes made by saravana line322,line324
async def generate_qr(amount: str) -> Dict:
    print("serive qr serive !!!!!!!!!!!!!!!!!! - vpa_service.py:320",amount)
    access_token = await get_valid_access_token()
    txn_id = await generate_unique_ext_txn_id()
    now = datetime.utcnow()
    await execute(
        """
        INSERT INTO transactions (
            order_id,
            ext_transaction_id,
            amount,
            status,
            qr_string,
            created_at,
            updated_at
        )
        VALUES (
            :order_id,
            :ext_transaction_id,
            :amount,
            :status,
            :qr_string,
            :created_at,
            :updated_at
        )
        """,
        {
            "order_id": None,
            "ext_transaction_id": txn_id,
            "amount": float(amount),
            "status": "PENDING",
            "qr_string": None,
            "created_at": now,
            "updated_at": now
        }
    )
    
    print("access_token - vpa_service.py:323",access_token)
    # 🔹 STEP 1: REQUEST DATA
    request_data = {
    "amount": amount,
    "extTransactionId": txn_id,
    "channel": "API",
    "remark": "QR SIT",
    "source": "MIDCPRIN01",
    "terminalId": "TRDCIN0001",
    "type": "D",
    "sid": "SIDCIN0001",
    "upiId": "mrch.midcprin01.sidcin0001.trdcin0001@cnrb",
    "requestTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "reciept": "https://google.com",
    "checksum": ""
}

    # 🔹 STEP 2: SIGN PAYLOAD
    plain_payload = {
        "Request": {
            "body": {
                "encryptData": request_data
            }
        }
    }

    payload_str_for_sign = json.dumps(
        plain_payload,
        separators=(",", ":"),
        ensure_ascii=False
    )

    print("SIGN PAYLOAD (QR): - vpa_service.py:355", payload_str_for_sign)

    signature = sign_payload(payload_str_for_sign)
    print("SIGNATURE (QR): - vpa_service.py:358", signature)

    # 🔹 STEP 3: ENCRYPT
    encrypted_string = encrypt_data(request_data)
    print("ENCRYPTED (QR): - vpa_service.py:362", encrypted_string)

    # 🔹 STEP 4: FINAL PAYLOAD
    final_payload = {
        "Request": {
            "body": {
                "encryptData": encrypted_string
            }
        }
    }

    payload_str = json.dumps(final_payload, separators=(",", ":"))
    print("FINAL PAYLOAD (QR): - vpa_service.py:374", payload_str)

    # 🔹 STEP 5: HEADERS
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-client-certificate": PUBLIC_KEY.strip(),
        "x-api-interaction-id": str(uuid.uuid4()),
        "x-timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-signature": signature,
        "x-forwarded-for": CLIENT_IP,
    }

    print("HEADERS (QR): - vpa_service.py:390", headers)

    # 🔹 STEP 6: API CALL
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            QR_GENERATION_URL,
            headers=headers,
            content=payload_str
        )

    print("STATUS (QR): - vpa_service.py:400", response.status_code)
    print("RAW RESPONSE (QR): - vpa_service.py:401", response.text)

    # 🔹 STEP 7: DECRYPT RESPONSE
    # 7️⃣ Decrypt response
    try:
        resp_json = response.json()
        encrypted_resp = resp_json["Response"]["body"]["encryptData"]
        decrypted_resp = decrypt_data(encrypted_resp)

        # Use API-provided qrString if available, otherwise fallback to manual
        qr_string = decrypted_resp.get(
            "qrString",
            build_clean_upi_qr(
                upi_id=request_data["upiId"],
                name="RNFMID Merchant",
                amount=amount,
                txn_id=txn_id,
                note=request_data["remark"]
            )
        )
        
        await execute(
            """
            UPDATE transactions
            SET qr_string = :qr_string,
                updated_at = NOW()
            WHERE ext_transaction_id = :txn_id
            """,
            {
                "qr_string": qr_string,
                "txn_id": txn_id
            }
        )
        
        qr_image = generate_qr_image(qr_string)

        return {
            "transaction_id": txn_id,
            "qr_string": qr_string,
            "qr_image": qr_image,
            "decrypted_response": decrypted_resp
        }

    except Exception as e:
        await execute(
            """
            UPDATE transactions
            SET status = 'FAILED',
                updated_at = NOW()
            WHERE ext_transaction_id = :txn_id
            """,
            {"txn_id": txn_id}
        )


        return {
            "status": response.status_code,
            "raw": response.text,
            "error": str(e)
        }
    



def generate_qr_image(qr_string: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=None,
        box_size=10,
        border=4
    )
    qr.add_data(qr_string)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def build_clean_upi_qr(upi_id: str, name: str, amount: str, txn_id: str, note: str) -> str:
    """
    Build GooglePay/PhonePe compatible UPI QR string
    """

    return (
        f"upi://pay?"
        f"pa={upi_id}&"
        f"pn={quote(name)}&"
        f"am={amount}&"
        f"cu=INR&"
        f"tn={quote(note)}&"
        f"tr={txn_id}"
    )


async def get_qr_status_rrn(access_token: str, rrn: str) -> Dict:
    try:
        # 🔹 STEP 1: REQUEST DATA
        request_data = {
            "rrn": rrn,
            "channel": "api",
            "terminalId": "TRDCIN0001",   # keep same as QR generate
            "mid": "MIDCPRIN01",
            "sid": "SIDCIN0001",
            "checksum": ""
        }

        # 🔹 STEP 2: SIGN PAYLOAD (PLAIN JSON, NOT ENCRYPTED)
        plain_payload = {
            "Request": {
                "body": {
                    "encryptData": request_data
                }
            }
        }

        payload_str_for_sign = json.dumps(
            plain_payload,
            separators=(",", ":"),
            ensure_ascii=False
        )

        print("SIGN PAYLOAD (QR STATUS): - vpa_service.py:498", payload_str_for_sign)

        signature = sign_payload(payload_str_for_sign)
        print("SIGNATURE (QR STATUS): - vpa_service.py:501", signature)

        # 🔹 STEP 3: ENCRYPT REQUEST DATA
        encrypted_string = encrypt_data(request_data)
        print("ENCRYPTED (QR STATUS): - vpa_service.py:505", encrypted_string)

        # 🔹 STEP 4: FINAL PAYLOAD
        final_payload = {
            "Request": {
                "body": {
                    "encryptData": encrypted_string
                }
            }
        }

        payload_str = json.dumps(final_payload, separators=(",", ":"))
        print("FINAL PAYLOAD (QR STATUS): - vpa_service.py:517", payload_str)

        # 🔹 STEP 5: HEADERS
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-client-id": CLIENT_ID,
            "x-client-secret": CLIENT_SECRET,
            "x-client-certificate": PUBLIC_KEY.strip(),
            "x-api-interaction-id": str(uuid.uuid4()),
            "x-timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-signature": signature,
            "x-forwarded-for": CLIENT_IP,
        }

        print("HEADERS (QR STATUS): - vpa_service.py:533", headers)

        # 🔹 STEP 6: API CALL
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.canara.bank.in/v1/upi/qrstatus-rrn",
                headers=headers,
                content=payload_str
            )

        print("STATUS (QR STATUS): - vpa_service.py:543", response.status_code)
        print("RAW RESPONSE (QR STATUS): - vpa_service.py:544", response.text)

        # 🔹 STEP 7: DECRYPT RESPONSE
        try:
            resp_json = response.json()

            encrypted_resp = resp_json["Response"]["body"]["encryptData"]
            print("ENCRYPTED RESPONSE (QR STATUS): - vpa_service.py:551", encrypted_resp)

            decrypted_resp = decrypt_data(encrypted_resp)

            print("DECRYPTED RESPONSE (QR STATUS): - vpa_service.py:555", decrypted_resp)

            return decrypted_resp

        except Exception as e:
            print("DECRYPT ERROR (QR STATUS): - vpa_service.py:560", str(e))
            return {
                "status": response.status_code,
                "raw": response.text
            }

    except Exception as e:
        print("ERROR (QR STATUS): - vpa_service.py:567", str(e))
        return {"error": str(e)}
    
EXT_TRANSACTION_ID_URL = "https://api.canara.bank.in/v1/upi/qrstatus-extid"


async def get_qr_status_extid(access_token: str, ext_transaction_id: str) -> Dict:
    try:
        # 🔹 STEP 1: REQUEST DATA
        request_data = {
            "mid": "MIDCPRIN01",
            "channel": "api",
            "sid": "SIDCIN0001",
            "terminalId": "TRDCIN0001",
            "extTransactionId": ext_transaction_id,
            "checksum": ""
        }

        # 🔹 STEP 2: SIGN PAYLOAD (PLAIN JSON)
        plain_payload = {
            "Request": {
                "body": {
                    "encryptData": request_data
                }
            }
        }

        payload_str_for_sign = json.dumps(
            plain_payload,
            separators=(",", ":"),
            ensure_ascii=False
        )

        print("SIGN PAYLOAD (EXTID): - vpa_service.py:600", payload_str_for_sign)

        signature = sign_payload(payload_str_for_sign)
        print("SIGNATURE (EXTID): - vpa_service.py:603", signature)

        # 🔹 STEP 3: ENCRYPT DATA
        encrypted_string = encrypt_data(request_data)
        print("ENCRYPTED (EXTID): - vpa_service.py:607", encrypted_string)

        # 🔹 STEP 4: FINAL PAYLOAD
        final_payload = {
            "Request": {
                "body": {
                    "encryptData": encrypted_string
                }
            }
        }

        payload_str = json.dumps(final_payload, separators=(",", ":"))
        print("FINAL PAYLOAD (EXTID): - vpa_service.py:619", payload_str)

        # 🔹 STEP 5: FIX CLIENT SECRET TYPE
        client_secret = (
            CLIENT_SECRET.decode()
            if isinstance(CLIENT_SECRET, bytes)
            else CLIENT_SECRET
        )

        # 🔹 STEP 6: HEADERS
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-client-id": CLIENT_ID,
            "x-client-secret": client_secret,
            "x-client-certificate": PUBLIC_KEY.strip(),
            "x-api-interaction-id": str(uuid.uuid4()),
            "x-timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-signature": signature,
            "x-forwarded-for": CLIENT_IP,
        }

        print("HEADERS (EXTID): - vpa_service.py:642", headers)

        # 🔹 STEP 7: API CALL
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                EXT_TRANSACTION_ID_URL,
                headers=headers,
                content=payload_str
            )

        print("STATUS (EXTID): - vpa_service.py:652", response.status_code)
        print("RAW RESPONSE (EXTID): - vpa_service.py:653", response.text)

        # 🔹 STEP 8: DECRYPT RESPONSE
        try:
            resp_json = response.json()

            encrypted_resp = resp_json["Response"]["body"]["encryptData"]
            print("ENCRYPTED RESPONSE (EXTID): - vpa_service.py:660", encrypted_resp)

            decrypted_resp = decrypt_data(encrypted_resp)
            print("DECRYPTED RESPONSE (EXTID): - vpa_service.py:663", decrypted_resp)

            return decrypted_resp

        except Exception as e:
            print("DECRYPT ERROR (EXTID): - vpa_service.py:668", str(e))
            return {
                "status": response.status_code,
                "raw": response.text
            }

    except Exception as e:
        print("ERROR (EXTID): - vpa_service.py:675", str(e))
        return {"error": str(e)}
    


QR_STATEMENT_URL = "https://api.canara.bank.in/v1/upi/qrstmt"


async def get_qr_statement(
    access_token: str,
    start_date: str,
    end_date: str,
    page_size: str = "500",
    page_no: str = "0"
) -> Dict:
    try:
        # STEP 1: REQUEST DATA
        request_data = {
            "mid": "MIDCPRIN01",
            "sid": "SIDCIN0001",
            "terminalId": "",  # keep empty or same as configured
            "startDate": start_date,
            "endDate": end_date,
            "pageSize": page_size,
            "pageNo": page_no,
            "checksum": ""
        }

        # STEP 2: SIGN PAYLOAD
        plain_payload = {
            "Request": {
                "body": {
                    "encryptData": request_data
                }
            }
        }

        payload_str_for_sign = json.dumps(
            plain_payload,
            separators=(",", ":"),
            ensure_ascii=False
        )

        print("SIGN PAYLOAD (QR STMT): - vpa_service.py:718", payload_str_for_sign)

        signature = sign_payload(payload_str_for_sign)
        print("SIGNATURE (QR STMT): - vpa_service.py:721", signature)

        #STEP 3: ENCRYPT
        encrypted_string = encrypt_data(request_data)
        print("ENCRYPTED (QR STMT): - vpa_service.py:725", encrypted_string)

        #STEP 4: FINAL PAYLOAD
        final_payload = {
            "Request": {
                "body": {
                    "encryptData": encrypted_string
                }
            }
        }

        payload_str = json.dumps(final_payload, separators=(",", ":"))
        print("FINAL PAYLOAD (QR STMT): - vpa_service.py:737", payload_str)

        #STEP 5: FIX CLIENT SECRET TYPE
        client_secret = (
            CLIENT_SECRET.decode()
            if isinstance(CLIENT_SECRET, bytes)
            else CLIENT_SECRET
        )

        #STEP 6: HEADERS
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-client-id": CLIENT_ID,
            "x-client-secret": client_secret,
            "x-client-certificate": PUBLIC_KEY.strip(),
            "x-api-interaction-id": str(uuid.uuid4()),
            "x-timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-signature": signature,
            "x-forwarded-for": CLIENT_IP,
        }

        print("HEADERS (QR STMT): - vpa_service.py:760", headers)

        #STEP 7: API CALL
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                QR_STATEMENT_URL,
                headers=headers,
                content=payload_str
            )

        print("STATUS (QR STMT): - vpa_service.py:770", response.status_code)
        print("RAW RESPONSE (QR STMT): - vpa_service.py:771", response.text)

        #STEP 8: DECRYPT RESPONSE
        try:
            resp_json = response.json()

            encrypted_resp = resp_json["Response"]["body"]["encryptData"]
            print("ENCRYPTED RESPONSE (QR STMT): - vpa_service.py:778", encrypted_resp)

            decrypted_resp = decrypt_data(encrypted_resp)
            print("DECRYPTED RESPONSE (QR STMT): - vpa_service.py:781", decrypted_resp)

            return decrypted_resp

        except Exception as e:
            print("DECRYPT ERROR (QR STMT): - vpa_service.py:786", str(e))
            return {
                "status": response.status_code,
                "raw": response.text
            }

    except Exception as e:
        print("ERROR (QR STMT): - vpa_service.py:793", str(e))
        return {"error": str(e)}
        
        
logger = logging.getLogger(__name__)

import traceback

async def process_qr_callback(payload: Dict) -> Dict:
    try:
        # -------------------------------------------------
        # 🔹 STEP 1: Extract encrypted data
        # -------------------------------------------------
        encrypted_data = (
            payload.get("Request", {})
                   .get("body", {})
                   .get("encryptData")
        )

        if not encrypted_data:
            raise ValueError("Missing encryptData")

        print("ENCRYPTED CALLBACK:", encrypted_data)

        # -------------------------------------------------
        # 🔐 STEP 2: Decrypt
        # -------------------------------------------------
        decrypted = decrypt_data(encrypted_data)
        print("DECRYPTED CALLBACK:", decrypted)

        # -------------------------------------------------
        # 🔹 STEP 3: Extract fields
        # -------------------------------------------------
        ext_transaction_id = decrypted.get("extTransactionId")
        status = decrypted.get("status")
        amount = decrypted.get("amount")
        rrn = decrypted.get("rrn")
        txn_id = decrypted.get("txnId")
        customer_vpa = decrypted.get("customer_vpa")

        # -------------------------------------------------
        # 🔹 STEP 4: Validation
        # -------------------------------------------------
        if not ext_transaction_id or not status:
            raise ValueError("Missing required fields")

        # -------------------------------------------------
        # 🔥 STEP 5: Idempotency check (SAFE VERSION)
        # -------------------------------------------------
        existing = await query("""
            SELECT status FROM transactions
            WHERE ext_transaction_id = :ext_transaction_id
        """, {
            "ext_transaction_id": ext_transaction_id
        })

        print("DB RESULT:", existing, type(existing))

        row = None

        # Handle all possible return formats
        if isinstance(existing, list) and len(existing) > 0:
            row = existing[0]

        elif isinstance(existing, dict):
            row = existing

        elif existing in (None, 0, "0"):
            row = None

        else:
            print("⚠️ Unexpected DB format:", existing)

        # Idempotency check
        if row and row.get("status") == "SUCCESS":
            print("⚠️ Already processed, skipping")
            return {"status": "SUCCESS"}

        # -------------------------------------------------
        # 🔹 STEP 6: Business Logic
        # -------------------------------------------------
        if status == "SUCCESS":
            print(f"✅ SUCCESS: {ext_transaction_id}")

            await execute("""
                UPDATE transactions
                SET 
                    status = :status,
                    rrn = :rrn,
                    txn_id = :txn_id,
                    customer_vpa = :customer_vpa,
                    paid_at = NOW()
                WHERE ext_transaction_id = :ext_transaction_id
            """, {
                "status": "SUCCESS",
                "rrn": rrn,
                "txn_id": txn_id,
                "customer_vpa": customer_vpa,
                "ext_transaction_id": ext_transaction_id
            })

        elif status in ["FAILURE", "FAILED"]:
            print(f"❌ FAILED: {ext_transaction_id}")

            await execute("""
                UPDATE transactions
                SET 
                    status = :status,
                    txn_id = :txn_id,
                    customer_vpa = :customer_vpa
                WHERE ext_transaction_id = :ext_transaction_id
            """, {
                "status": "FAILED",
                "txn_id": txn_id,
                "customer_vpa": customer_vpa,
                "ext_transaction_id": ext_transaction_id
            })

        else:
            print(f"⏳ PENDING: {ext_transaction_id}")

        return {"status": "SUCCESS"}

    except Exception as e:
        print("PROCESS CALLBACK ERROR:", repr(e))
        traceback.print_exc()
        raise
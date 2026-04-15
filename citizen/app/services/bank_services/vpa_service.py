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

from app.services.bank_services.oauth_service import get_valid_access_token


API_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation"  #  FROM YOUR LOG
VPA_ENQUIRY_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation-enq"
QR_GENERATION_URL = "https://api.canarauat.bank.in/v1/upi/qr-generation"

CLIENT_ID = "AUx27zglhuuiRxahKUTmpAVEVKuJ3rsr"
CLIENT_SECRET =  b"B7WgKfGeURXYkEgRA1ZASYRFtUG64SEn"

# PUBLIC_KEY = "MIIDvzCCAqcCFAVhG9nlbXeEi19I2ad0MPUbYhsRMA0GCSqGSIb3DQEBCwUAMIGbMQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGFtaWxuYWR1MRAwDgYDVQQHDAdDaGVubmFpMRYwFAYDVQQKDA1DaXRpemVucHJpbnRzMQswCQYDVQQLDAJJVDEZMBcGA1UEAwwQY2l0aXplbnByaW50ei5pbjEmMCQGCSqGSIb3DQEJARYXY2l0aXplbnByaW50c0BnbWFpbC5jb20wHhcNMjYwMzEwMTE0MDIwWhcNMjcwMzEwMTE0MDIwWjCBmzELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRhbWlsbmFkdTEQMA4GA1UEBwwHQ2hlbm5haTEWMBQGA1UECgwNQ2l0aXplbnByaW50czELMAkGA1UECwwCSVQxGTAXBgNVBAMMEGNpdGl6ZW5wcmludHouaW4xJjAkBgkqhkiG9w0BCQEWF2NpdGl6ZW5wcmludHNAZ21haWwuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqppbQSbJSsvHfY1XFc52LyzfD6TOpdlkR/Gr41RNNtKQSgosMrUk249EINxfs81/NQUtCzXl3fdI1ZJXwqWVoJ/cwSnToHAGnX0WyqKnBomXl+yD4tMt2m9KYXkGIx2sKrvQiN9OTebOJGDiE/lk6jsFLGfD1v22egpK1o2Myx5JZTVhVWQgurEelLlig1TWFnk+oBrYsr4q8Ur749eoLNP1e00tqeArIStRqDAVJDr/H8K7Esng6g0XeadblIw+crx6Qcb0CuoLE4oweTDIAreZWnsc3xV3AbwFTPLSc0CwSFnt7f8g3qqV+r6GJl/kI7Gvb8vN/3HnooFtT/0oyQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCl8DuzsNM/lRm7zKBPRCScO/bj3MicSqIkN7KxDg1JxfTWBE1L2SyyxH5+eP4t1GBrZOFxZ6l167dc/HQub4SYP3eb/XvjZJJ2MEYWAWiHVf9rD6uFZdXuDvryLyDgWomz5kaULRHuhIjQqxypuMnMAjf5Gq8bIRgHSsP0TKQxeZeoXrtx9aZxrBS4gpnt41v6KqeZGnLdOJY7uNE8mDrFZnOeWDIh2chs/z5zPFLEHkK46TqXmnyKIH7S6/oSmTo0zHSPFWk0XwjhgQMqYRd4ydGesL6hnakiK41nassgOIpZWt1AysqIzH3kNhOo43LL0PA5qD/g1C4boZpW1AS4"
PUBLIC_KEY = "MIIDvzCCAqcCFAVhG9nlbXeEi19I2ad0MPUbYhsRMA0GCSqGSIb3DQEBCwUAMIGbMQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGFtaWxuYWR1MRAwDgYDVQQHDAdDaGVubmFpMRYwFAYDVQQKDA1DaXRpemVucHJpbnRzMQswCQYDVQQLDAJJVDEZMBcGA1UEAwwQY2l0aXplbnByaW50ei5pbjEmMCQGCSqGSIb3DQEJARYXY2l0aXplbnByaW50c0BnbWFpbC5jb20wHhcNMjYwMzEwMTE0MDIwWhcNMjcwMzEwMTE0MDIwWjCBmzELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRhbWlsbmFkdTEQMA4GA1UEBwwHQ2hlbm5haTEWMBQGA1UECgwNQ2l0aXplbnByaW50czELMAkGA1UECwwCSVQxGTAXBgNVBAMMEGNpdGl6ZW5wcmludHouaW4xJjAkBgkqhkiG9w0BCQEWF2NpdGl6ZW5wcmludHNAZ21haWwuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqppbQSbJSsvHfY1XFc52LyzfD6TOpdlkR/Gr41RNNtKQSgosMrUk249EINxfs81/NQUtCzXl3fdI1ZJXwqWVoJ/cwSnToHAGnX0WyqKnBomXl+yD4tMt2m9KYXkGIx2sKrvQiN9OTebOJGDiE/lk6jsFLGfD1v22egpK1o2Myx5JZTVhVWQgurEelLlig1TWFnk+oBrYsr4q8Ur749eoLNP1e00tqeArIStRqDAVJDr/H8K7Esng6g0XeadblIw+crx6Qcb0CuoLE4oweTDIAreZWnsc3xV3AbwFTPLSc0CwSFnt7f8g3qqV+r6GJl/kI7Gvb8vN/3HnooFtT/0oyQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCl8DuzsNM/lRm7zKBPRCScO/bj3MicSqIkN7KxDg1JxfTWBE1L2SyyxH5+eP4t1GBrZOFxZ6l167dc/HQub4SYP3eb/XvjZJJ2MEYWAWiHVf9rD6uFZdXuDvryLyDgWomz5kaULRHuhIjQqxypuMnMAjf5Gq8bIRgHSsP0TKQxeZeoXrtx9aZxrBS4gpnt41v6KqeZGnLdOJY7uNE8mDrFZnOeWDIh2chs/z5zPFLEHkK46TqXmnyKIH7S6/oSmTo0zHSPFWk0XwjhgQMqYRd4ydGesL6hnakiK41nassgOIpZWt1AysqIzH3kNhOo43LL0PA5qD/g1C4boZpW1AS4"
SYMMETRIC_KEY = bytes.fromhex(
    "0c5b95196e8e306eff0b6a9e0d37c878806954401620f2a4a30fbd0f031697e8"
)

PRIVATE_KEY_PATH = Path(__file__).resolve().parents[3] / "private_key.pem"  # Adjust path as needed
CLIENT_IP = "54.206.3.97"


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
    print("JWE PARTS COUNT: - vpa_service.py:97", len(parts))  # must be 5

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

    print("DECRYPTED STRING: - vpa_service.py:114", decrypted_payload)

    return json.loads(decrypted_payload)
# ================= CREATE VPA =================
async def create_vpa(access_token: str) -> Dict:

    #STEP 1: RAW DATA
    request_data = {
        "mid": "RNFMID0001",
        "channel": "API",
        "account_number": "120003067568",
        "mobile_number": "9003088363",
        "terminalId": "TRDCIP0001",
        "name": "Dynamicqrcode",
        "bank_name": "Canara Bank",
        "mcc": "5411",
        "ifsc_code": "CNRF0016044",
        "checksum": "",
        "additionalNo": " ",
        "sid": "SIDCIP0001"
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

    print("SIGN PAYLOAD: - vpa_service.py:151", payload_str_for_sign)

    signature = sign_payload(payload_str_for_sign)
    print("SIGNATURE: - vpa_service.py:154", signature)

    # 🔹 STEP 3: ENCRYPT ONLY request_data
    encrypted_string = encrypt_data(request_data)
    print("ENCRYPTED: - vpa_service.py:158", encrypted_string)

    # 🔹 STEP 4: FINAL PAYLOAD
    final_payload = {
        "Request": {
            "body": {
                "encryptData": encrypted_string
            }
        }
    }

    payload_str = json.dumps(final_payload, separators=(",", ":"))
    print("FINAL PAYLOAD: - vpa_service.py:170", payload_str)

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

    print("HEADERS: - vpa_service.py:186", headers)

    #STEP 6: API CALL
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            API_URL,
            headers=headers,
            content=payload_str
        )

    # 🔍 DEBUG RESPONSE
    print("STATUS: - vpa_service.py:197", response.status_code)
    print("RAW RESPONSE: - vpa_service.py:198", response.text)

    try:
        resp_json = response.json()

        encrypted_resp = resp_json["Response"]["body"]["encryptData"]
        print("ENCRYPTED RESPONSE: - vpa_service.py:204", encrypted_resp)

        decrypted_resp = decrypt_data(encrypted_resp)

        print("DECRYPTED RESPONSE: - vpa_service.py:208", decrypted_resp)

        return decrypted_resp

    except Exception as e:
        print("DECRYPT ERROR: - vpa_service.py:213", str(e))
        return {
            "status": response.status_code,
            "raw": response.text
        }
    
async def vpa_inquiry(access_token: str, batch_id: str) -> Dict:

    # 🔹 STEP 1: REQUEST DATA (ONLY CHANGE FROM CREATE API)
    request_data = {
        "channel": "API",
        "mid": "RNFMID0001",
        "terminalId": "TRDCIP0001",
        "sid": "SIDCIP0001",
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

    print("SIGN PAYLOAD (ENQ): - vpa_service.py:246", payload_str_for_sign)

    signature = sign_payload(payload_str_for_sign)
    print("SIGNATURE (ENQ): - vpa_service.py:249", signature)

    # 🔹 STEP 3: ENCRYPT ONLY request_data
    encrypted_string = encrypt_data(request_data)
    print("ENCRYPTED (ENQ): - vpa_service.py:253", encrypted_string)

    # 🔹 STEP 4: FINAL PAYLOAD
    final_payload = {
        "Request": {
            "body": {
                "encryptData": encrypted_string
            }
        }
    }

    payload_str = json.dumps(final_payload, separators=(",", ":"))
    print("FINAL PAYLOAD (ENQ): - vpa_service.py:265", payload_str)

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

    print("HEADERS (ENQ): - vpa_service.py:281", headers)

    # 🔹 STEP 6: API CALL
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            VPA_ENQUIRY_URL,
            headers=headers,
            content=payload_str
        )

    print("STATUS (ENQ): - vpa_service.py:291", response.status_code)
    print("RAW RESPONSE (ENQ): - vpa_service.py:292", response.text)

    # 🔹 STEP 7: DECRYPT RESPONSE
    try:
        resp_json = response.json()

        encrypted_resp = resp_json["Response"]["body"]["encryptData"]
        print("ENCRYPTED RESPONSE (ENQ): - vpa_service.py:299", encrypted_resp)

        decrypted_resp = decrypt_data(encrypted_resp)

        print("DECRYPTED RESPONSE (ENQ): - vpa_service.py:303", decrypted_resp)

        return decrypted_resp

    except Exception as e:
        print("DECRYPT ERROR (ENQ): - vpa_service.py:308", str(e))
        return {
            "status": response.status_code,
            "raw": response.text
        }

extTransactionId = (
    f"EXT{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
)[:35]

async def generate_qr(amount: str) -> Dict:
    print("serive qr serive !!!!!!!!!!!!!!!!!! - vpa_service.py:319",amount)
    access_token = await get_valid_access_token()

    print("access_token - vpa_service.py:322",access_token)
    # 🔹 STEP 1: REQUEST DATA
    request_data = {
    "amount": amount,
    "extTransactionId": extTransactionId,
    "channel": "API",
    "remark": "QR SIT testing",
    "source": "RNFMID0001",
    "terminalId": "TRDCIP0001",
    "type": "D",
    "sid": "SIDCIP0001",
    "upiId": "rnf.rnfmid0001.sidcip0001.trdcip0001@cnrf",
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

    print("SIGN PAYLOAD (QR): - vpa_service.py:354", payload_str_for_sign)

    signature = sign_payload(payload_str_for_sign)
    print("SIGNATURE (QR): - vpa_service.py:357", signature)

    # 🔹 STEP 3: ENCRYPT
    encrypted_string = encrypt_data(request_data)
    print("ENCRYPTED (QR): - vpa_service.py:361", encrypted_string)

    # 🔹 STEP 4: FINAL PAYLOAD
    final_payload = {
        "Request": {
            "body": {
                "encryptData": encrypted_string
            }
        }
    }

    payload_str = json.dumps(final_payload, separators=(",", ":"))
    print("FINAL PAYLOAD (QR): - vpa_service.py:373", payload_str)

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

    print("HEADERS (QR): - vpa_service.py:389", headers)

    # 🔹 STEP 6: API CALL
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            QR_GENERATION_URL,
            headers=headers,
            content=payload_str
        )

    print("STATUS (QR): - vpa_service.py:399", response.status_code)
    print("RAW RESPONSE (QR): - vpa_service.py:400", response.text)

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
                txn_id=extTransactionId,
                note=request_data["remark"]
            )
        )

        # Generate QR image
        qr_image = generate_qr_image(qr_string)

        return {
            "decrypted_response": decrypted_resp,
            "qr_string": qr_string,
            "qr_image": qr_image
        }

    except Exception as e:
        return {"status": response.status_code, "raw": response.text, "error": str(e)}
    



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
            "terminalId": "TRDCIP0001",   # keep same as QR generate
            "mid": "RNFMID0001",
            "sid": "SIDCIP0001",
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

        print("SIGN PAYLOAD (QR STATUS): - vpa_service.py:497", payload_str_for_sign)

        signature = sign_payload(payload_str_for_sign)
        print("SIGNATURE (QR STATUS): - vpa_service.py:500", signature)

        # 🔹 STEP 3: ENCRYPT REQUEST DATA
        encrypted_string = encrypt_data(request_data)
        print("ENCRYPTED (QR STATUS): - vpa_service.py:504", encrypted_string)

        # 🔹 STEP 4: FINAL PAYLOAD
        final_payload = {
            "Request": {
                "body": {
                    "encryptData": encrypted_string
                }
            }
        }

        payload_str = json.dumps(final_payload, separators=(",", ":"))
        print("FINAL PAYLOAD (QR STATUS): - vpa_service.py:516", payload_str)

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

        print("HEADERS (QR STATUS): - vpa_service.py:532", headers)

        # 🔹 STEP 6: API CALL
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.canarauat.bank.in/v1/upi/qrstatus-rrn",
                headers=headers,
                content=payload_str
            )

        print("STATUS (QR STATUS): - vpa_service.py:542", response.status_code)
        print("RAW RESPONSE (QR STATUS): - vpa_service.py:543", response.text)

        # 🔹 STEP 7: DECRYPT RESPONSE
        try:
            resp_json = response.json()

            encrypted_resp = resp_json["Response"]["body"]["encryptData"]
            print("ENCRYPTED RESPONSE (QR STATUS): - vpa_service.py:550", encrypted_resp)

            decrypted_resp = decrypt_data(encrypted_resp)

            print("DECRYPTED RESPONSE (QR STATUS): - vpa_service.py:554", decrypted_resp)

            return decrypted_resp

        except Exception as e:
            print("DECRYPT ERROR (QR STATUS): - vpa_service.py:559", str(e))
            return {
                "status": response.status_code,
                "raw": response.text
            }

    except Exception as e:
        print("ERROR (QR STATUS): - vpa_service.py:566", str(e))
        return {"error": str(e)}
    
EXT_TRANSACTION_ID_URL = "https://api.canarauat.bank.in/v1/upi/qrstatus-extid"


async def get_qr_status_extid(access_token: str, ext_transaction_id: str) -> Dict:
    try:
        # 🔹 STEP 1: REQUEST DATA
        request_data = {
            "mid": "RNFMID0001",
            "channel": "api",
            "sid": "SIDCIP0001",
            "terminalId": "TRDCIP0001",
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

        print("SIGN PAYLOAD (EXTID): - vpa_service.py:599", payload_str_for_sign)

        signature = sign_payload(payload_str_for_sign)
        print("SIGNATURE (EXTID): - vpa_service.py:602", signature)

        # 🔹 STEP 3: ENCRYPT DATA
        encrypted_string = encrypt_data(request_data)
        print("ENCRYPTED (EXTID): - vpa_service.py:606", encrypted_string)

        # 🔹 STEP 4: FINAL PAYLOAD
        final_payload = {
            "Request": {
                "body": {
                    "encryptData": encrypted_string
                }
            }
        }

        payload_str = json.dumps(final_payload, separators=(",", ":"))
        print("FINAL PAYLOAD (EXTID): - vpa_service.py:618", payload_str)

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

        print("HEADERS (EXTID): - vpa_service.py:641", headers)

        # 🔹 STEP 7: API CALL
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                EXT_TRANSACTION_ID_URL,
                headers=headers,
                content=payload_str
            )

        print("STATUS (EXTID): - vpa_service.py:651", response.status_code)
        print("RAW RESPONSE (EXTID): - vpa_service.py:652", response.text)

        # 🔹 STEP 8: DECRYPT RESPONSE
        try:
            resp_json = response.json()

            encrypted_resp = resp_json["Response"]["body"]["encryptData"]
            print("ENCRYPTED RESPONSE (EXTID): - vpa_service.py:659", encrypted_resp)

            decrypted_resp = decrypt_data(encrypted_resp)
            print("DECRYPTED RESPONSE (EXTID): - vpa_service.py:662", decrypted_resp)

            return decrypted_resp

        except Exception as e:
            print("DECRYPT ERROR (EXTID): - vpa_service.py:667", str(e))
            return {
                "status": response.status_code,
                "raw": response.text
            }

    except Exception as e:
        print("ERROR (EXTID): - vpa_service.py:674", str(e))
        return {"error": str(e)}
    


QR_STATEMENT_URL = "https://api.canarauat.bank.in/v1/upi/qrstmt"


async def get_qr_statement(
    access_token: str,
    start_date: str,
    end_date: str,
    page_size: str = "5",
    page_no: str = "1"
) -> Dict:
    try:
        # STEP 1: REQUEST DATA
        request_data = {
            "mid": "RNFMID0001",
            "sid": "SIDCIP0001",
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

        print("SIGN PAYLOAD (QR STMT): - vpa_service.py:717", payload_str_for_sign)

        signature = sign_payload(payload_str_for_sign)
        print("SIGNATURE (QR STMT): - vpa_service.py:720", signature)

        #STEP 3: ENCRYPT
        encrypted_string = encrypt_data(request_data)
        print("ENCRYPTED (QR STMT): - vpa_service.py:724", encrypted_string)

        #STEP 4: FINAL PAYLOAD
        final_payload = {
            "Request": {
                "body": {
                    "encryptData": encrypted_string
                }
            }
        }

        payload_str = json.dumps(final_payload, separators=(",", ":"))
        print("FINAL PAYLOAD (QR STMT): - vpa_service.py:736", payload_str)

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

        print("HEADERS (QR STMT): - vpa_service.py:759", headers)

        #STEP 7: API CALL
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                QR_STATEMENT_URL,
                headers=headers,
                content=payload_str
            )

        print("STATUS (QR STMT): - vpa_service.py:769", response.status_code)
        print("RAW RESPONSE (QR STMT): - vpa_service.py:770", response.text)

        #STEP 8: DECRYPT RESPONSE
        try:
            resp_json = response.json()

            encrypted_resp = resp_json["Response"]["body"]["encryptData"]
            print("ENCRYPTED RESPONSE (QR STMT): - vpa_service.py:777", encrypted_resp)

            decrypted_resp = decrypt_data(encrypted_resp)
            print("DECRYPTED RESPONSE (QR STMT): - vpa_service.py:780", decrypted_resp)

            return decrypted_resp

        except Exception as e:
            print("DECRYPT ERROR (QR STMT): - vpa_service.py:785", str(e))
            return {
                "status": response.status_code,
                "raw": response.text
            }

    except Exception as e:
        print("ERROR (QR STMT): - vpa_service.py:792", str(e))
        return {"error": str(e)}
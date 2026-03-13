# import json

# import httpx
# import random
# import string
# from app.services.bank_services.oauth_service import get_access_token

# API_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation"

# # Random alphanumeric generator
# def generate_random_id(prefix="", length=6):
#     chars = string.ascii_uppercase + string.digits
#     return prefix + ''.join(random.choices(chars, k=length))

# async def create_vpa(access_token: str):
#     # Get OAuth access token
#     if not access_token:
#         raise ValueError("Access token is required")


#     terminal_id = generate_random_id("TERM", 6)
#     sid = generate_random_id("SID", 6)

#     # Prepare request payload exactly as per API doc
#     request_data = {
#         "mid": "YOUTUBE001",
#         "channel": "api",
#         "account_number": "60441010001739",
#         "mobile_number": "9003088363",
#         "terminalId": terminal_id,
#         "name": "citizenprints",
#         "bank_name": "Canara Bank",
#         "mcc": "5411",
#         "ifsc_code": "CNRB0016044",
#         "checksum": "",        # Bank handles checksum
#         "additionalNo": "",    # Optional
#         "sid": sid
#     }

#     payload = {
#         "Request": {
#             "body": {
#                 "encryptData": json.dumps(request_data)  # <-- JSON string
#             }
#         }
#     }

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }

#     try:
#         async with httpx.AsyncClient(timeout=30) as client:
#             response = await client.post(API_URL, json=payload, headers=headers)

#         print("STATUS: - vpa_service.py:57", response.status_code)
#         print("BANK RESPONSE: - vpa_service.py:58", response.text)

#         # Try parsing JSON safely
#         try:
#             return response.json()
#         except json.JSONDecodeError:
#             raise Exception(f"Invalid JSON response: {response.text}")

#     except Exception as e:
#         print("e - vpa_service.py:67",)
#         raise Exception(f"VPA Creation Failed: {str(e)}")
    
import json
import time
import base64
from pathlib import Path
import httpx
import random
import string

from jose import jwe
from jose.constants import ALGORITHMS
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import uuid

API_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation"

CLIENT_ID = "AUx27zglhuuiRxahKUTmpAVEVKuJ3rsr"
CLIENT_SECRET = "B7WgKfGeURXYkEgRA1ZASYRFtUG64SEn"

PUBLIC_KEY = "MIIDvzCCAqcCFAVhG9nlbXeEi19I2ad0MPUbYhsRMA0GCSqGSIb3DQEBCwUAMIGbMQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGFtaWxuYWR1MRAwDgYDVQQHDAdDaGVubmFpMRYwFAYDVQQKDA1DaXRpemVucHJpbnRzMQswCQYDVQQLDAJJVDEZMBcGA1UEAwwQY2l0aXplbnByaW50ei5pbjEmMCQGCSqGSIb3DQEJARYXY2l0aXplbnByaW50c0BnbWFpbC5jb20wHhcNMjYwMzEwMTE0MDIwWhcNMjcwMzEwMTE0MDIwWjCBmzELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRhbWlsbmFkdTEQMA4GA1UEBwwHQ2hlbm5haTEWMBQGA1UECgwNQ2l0aXplbnByaW50czELMAkGA1UECwwCSVQxGTAXBgNVBAMMEGNpdGl6ZW5wcmludHouaW4xJjAkBgkqhkiG9w0BCQEWF2NpdGl6ZW5wcmludHNAZ21haWwuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqppbQSbJSsvHfY1XFc52LyzfD6TOpdlkR/Gr41RNNtKQSgosMrUk249EINxfs81/NQUtCzXl3fdI1ZJXwqWVoJ/cwSnToHAGnX0WyqKnBomXl+yD4tMt2m9KYXkGIx2sKrvQiN9OTebOJGDiE/lk6jsFLGfD1v22egpK1o2Myx5JZTVhVWQgurEelLlig1TWFnk+oBrYsr4q8Ur749eoLNP1e00tqeArIStRqDAVJDr/H8K7Esng6g0XeadblIw+crx6Qcb0CuoLE4oweTDIAreZWnsc3xV3AbwFTPLSc0CwSFnt7f8g3qqV+r6GJl/kI7Gvb8vN/3HnooFtT/0oyQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCl8DuzsNM/lRm7zKBPRCScO/bj3MicSqIkN7KxDg1JxfTWBE1L2SyyxH5+eP4t1GBrZOFxZ6l167dc/HQub4SYP3eb/XvjZJJ2MEYWAWiHVf9rD6uFZdXuDvryLyDgWomz5kaULRHuhIjQqxypuMnMAjf5Gq8bIRgHSsP0TKQxeZeoXrtx9aZxrBS4gpnt41v6KqeZGnLdOJY7uNE8mDrFZnOeWDIh2chs/z5zPFLEHkK46TqXmnyKIH7S6/oSmTo0zHSPFWk0XwjhgQMqYRd4ydGesL6hnakiK41nassgOIpZWt1AysqIzH3kNhOo43LL0PA5qD/g1C4boZpW1AS4"

SYMMETRIC_KEY = b"0c5b95196e8e306eff0b6a9e0d37c878806954401620f2a4a30fbd0f031697e8"


# ----------------------------
# Utility Functions
# ----------------------------

def generate_random_id(prefix="", length=6):
    chars = string.ascii_uppercase + string.digits
    return prefix + ''.join(random.choices(chars, k=length))


def digest(shared_symmetric_key):
    val = bytearray(
        int(shared_symmetric_key[i:i+2], 16)
        for i in range(0, len(shared_symmetric_key), 2)
    )
    return bytes(val)


def encrypt(input_text, shared_symmetric_key):
    encrypted = jwe.encrypt(
        input_text,
        key=shared_symmetric_key,
        encryption=ALGORITHMS.A128CBC_HS256,
        algorithm=ALGORITHMS.A256KW
    )
    return encrypted


def decrypt(input_data, shared_symmetric_key):
    decrypted = jwe.decrypt(input_data, shared_symmetric_key)
    return decrypted.decode("utf-8")


def sign(input_data):

    if isinstance(input_data, str):
        input_data = input_data.encode("utf-8")

    BASE_DIR = Path(__file__).resolve().parents[3]
    key_path = BASE_DIR / "citizen_prints_pem.pem"
    print("KEY PATH: - vpa_service.py:133", key_path)
    print("FILE EXISTS: - vpa_service.py:134", key_path.exists())
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    signature = private_key.sign(
        input_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode("utf-8")


# ----------------------------
# Main VPA Creation
# ----------------------------

async def create_vpa(access_token: str):

    terminal_id = generate_random_id("TERM")
    sid = generate_random_id("SID")

    encrypt_data = {
        "mid": "RNFMID0001",
        "channel": "api",
        "account_number": "60441010001739",
        "mobile_number": "9003088363",
        "terminalId": terminal_id,
        "name": "citizenprints",
        "bank_name": "Canara Bank",
        "mcc": "5411",
        "ifsc_code": "CNRB0016044",
        "checksum": "",
        "additionalNo": "",
        "sid": "RNFMID0001"
    }

    payload = {
        "Request": {
            "body": {
                "encryptData": encrypt_data
            }
        }
    }

    # ----------------------------
    # Encrypt Payload
    # ----------------------------

    encrypt_data_json = json.dumps(encrypt_data, separators=(',', ':'))

    aes_key = digest(SYMMETRIC_KEY)

    jwt = encrypt(encrypt_data_json, aes_key)

    payload["Request"]["body"]["encryptData"] = jwt.decode("utf-8")

    payload_json = json.dumps(payload, separators=(',', ':')).encode("utf-8")
    print("FINAL PAYLOAD: - vpa_service.py:195", json.dumps(payload, indent=2))
    # ------------------
    # Digital Signature
    # ----------------------------

    signature = sign(payload_json)
    print("ACCESS TOKEN USED: - vpa_service.py:201", access_token)

    headers = {
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-client-certificate": PUBLIC_KEY,
        "x-api-interaction-id": str(uuid.uuid4()),
        "x-timestamp": str(int(time.time())),
        "x-signature": signature,
        "Content-Type": "application/json"
    }
    print("ACCESS TOKEN USED: - vpa_service.py:212", headers)

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(
            API_URL,
            data=payload_json,
            headers=headers
        )

    print("STATUS: - vpa_service.py:222", response.status_code)
    print("ENCRYPTED RESPONSE: - vpa_service.py:223", response.text)

    try:

        response_json = response.json()

        encrypted_response = response_json["Response"]["body"]["encryptData"]

        decrypted = decrypt(encrypted_response, aes_key)

        decrypted_dict = json.loads(decrypted)

        return decrypted_dict

    except Exception as e:

        return {
            "error": str(e),
            "raw_response": response.text
        }
import json
import base64
import uuid
from datetime import datetime
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


API_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation"  # ✅ FROM YOUR LOG

CLIENT_ID = "AUx27zglhuuiRxahKUTmpAVEVKuJ3rsr"
CLIENT_SECRET = "B7WgKfGeURXYkEgRA1ZASYRFtUG64SEn"

# PUBLIC_KEY = "MIIDvzCCAqcCFAVhG9nlbXeEi19I2ad0MPUbYhsRMA0GCSqGSIb3DQEBCwUAMIGbMQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGFtaWxuYWR1MRAwDgYDVQQHDAdDaGVubmFpMRYwFAYDVQQKDA1DaXRpemVucHJpbnRzMQswCQYDVQQLDAJJVDEZMBcGA1UEAwwQY2l0aXplbnByaW50ei5pbjEmMCQGCSqGSIb3DQEJARYXY2l0aXplbnByaW50c0BnbWFpbC5jb20wHhcNMjYwMzEwMTE0MDIwWhcNMjcwMzEwMTE0MDIwWjCBmzELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRhbWlsbmFkdTEQMA4GA1UEBwwHQ2hlbm5haTEWMBQGA1UECgwNQ2l0aXplbnByaW50czELMAkGA1UECwwCSVQxGTAXBgNVBAMMEGNpdGl6ZW5wcmludHouaW4xJjAkBgkqhkiG9w0BCQEWF2NpdGl6ZW5wcmludHNAZ21haWwuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqppbQSbJSsvHfY1XFc52LyzfD6TOpdlkR/Gr41RNNtKQSgosMrUk249EINxfs81/NQUtCzXl3fdI1ZJXwqWVoJ/cwSnToHAGnX0WyqKnBomXl+yD4tMt2m9KYXkGIx2sKrvQiN9OTebOJGDiE/lk6jsFLGfD1v22egpK1o2Myx5JZTVhVWQgurEelLlig1TWFnk+oBrYsr4q8Ur749eoLNP1e00tqeArIStRqDAVJDr/H8K7Esng6g0XeadblIw+crx6Qcb0CuoLE4oweTDIAreZWnsc3xV3AbwFTPLSc0CwSFnt7f8g3qqV+r6GJl/kI7Gvb8vN/3HnooFtT/0oyQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCl8DuzsNM/lRm7zKBPRCScO/bj3MicSqIkN7KxDg1JxfTWBE1L2SyyxH5+eP4t1GBrZOFxZ6l167dc/HQub4SYP3eb/XvjZJJ2MEYWAWiHVf9rD6uFZdXuDvryLyDgWomz5kaULRHuhIjQqxypuMnMAjf5Gq8bIRgHSsP0TKQxeZeoXrtx9aZxrBS4gpnt41v6KqeZGnLdOJY7uNE8mDrFZnOeWDIh2chs/z5zPFLEHkK46TqXmnyKIH7S6/oSmTo0zHSPFWk0XwjhgQMqYRd4ydGesL6hnakiK41nassgOIpZWt1AysqIzH3kNhOo43LL0PA5qD/g1C4boZpW1AS4"
PUBLIC_KEY = "MIIDvzCCAqcCFAVhG9nlbXeEi19I2ad0MPUbYhsRMA0GCSqGSIb3DQEBCwUAMIGbMQswCQYDVQQGEwJJTjESMBAGA1UECAwJVGFtaWxuYWR1MRAwDgYDVQQHDAdDaGVubmFpMRYwFAYDVQQKDA1DaXRpemVucHJpbnRzMQswCQYDVQQLDAJJVDEZMBcGA1UEAwwQY2l0aXplbnByaW50ei5pbjEmMCQGCSqGSIb3DQEJARYXY2l0aXplbnByaW50c0BnbWFpbC5jb20wHhcNMjYwMzEwMTE0MDIwWhcNMjcwMzEwMTE0MDIwWjCBmzELMAkGA1UEBhMCSU4xEjAQBgNVBAgMCVRhbWlsbmFkdTEQMA4GA1UEBwwHQ2hlbm5haTEWMBQGA1UECgwNQ2l0aXplbnByaW50czELMAkGA1UECwwCSVQxGTAXBgNVBAMMEGNpdGl6ZW5wcmludHouaW4xJjAkBgkqhkiG9w0BCQEWF2NpdGl6ZW5wcmludHNAZ21haWwuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqppbQSbJSsvHfY1XFc52LyzfD6TOpdlkR/Gr41RNNtKQSgosMrUk249EINxfs81/NQUtCzXl3fdI1ZJXwqWVoJ/cwSnToHAGnX0WyqKnBomXl+yD4tMt2m9KYXkGIx2sKrvQiN9OTebOJGDiE/lk6jsFLGfD1v22egpK1o2Myx5JZTVhVWQgurEelLlig1TWFnk+oBrYsr4q8Ur749eoLNP1e00tqeArIStRqDAVJDr/H8K7Esng6g0XeadblIw+crx6Qcb0CuoLE4oweTDIAreZWnsc3xV3AbwFTPLSc0CwSFnt7f8g3qqV+r6GJl/kI7Gvb8vN/3HnooFtT/0oyQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCl8DuzsNM/lRm7zKBPRCScO/bj3MicSqIkN7KxDg1JxfTWBE1L2SyyxH5+eP4t1GBrZOFxZ6l167dc/HQub4SYP3eb/XvjZJJ2MEYWAWiHVf9rD6uFZdXuDvryLyDgWomz5kaULRHuhIjQqxypuMnMAjf5Gq8bIRgHSsP0TKQxeZeoXrtx9aZxrBS4gpnt41v6KqeZGnLdOJY7uNE8mDrFZnOeWDIh2chs/z5zPFLEHkK46TqXmnyKIH7S6/oSmTo0zHSPFWk0XwjhgQMqYRd4ydGesL6hnakiK41nassgOIpZWt1AysqIzH3kNhOo43LL0PA5qD/g1C4boZpW1AS4"
SYMMETRIC_KEY = "0c5b95196e8e306eff0b6a9e0d37c878806954401620f2a4a30fbd0f031697e8"


PRIVATE_KEY_PATH = Path(__file__).resolve().parents[3] / "citizen_prints_pem.pem"  # Adjust path as needed
CLIENT_IP = "54.206.3.97"


# ---------------- SIGN PAYLOAD ----------------
# def sign_payload_rsa_sha256(payload: dict, private_key_path: Path) -> str:
#     """
#     Sign JSON payload using RSA-SHA256 and return Base64 signature
#     """
#     message = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
#     with open(private_key_path, "rb") as f:
#         private_key = serialization.load_pem_private_key(f.read(), password=None)
#     signature = private_key.sign(
#         message,
#         padding.PKCS1v15(),
#         hashes.SHA256()
#     )
#     return base64.b64encode(signature).decode("utf-8")


# # ---------------- JWE ENCRYPTION ----------------
# def encrypt_jwe_aes_cbc_hs256(data: dict, bank_public_key_path: Path) -> str:
#     """
#     Encrypt the payload using AES-128-CBC + HMAC-SHA256 wrapped in JWE
#     Returns compact JWE string
#     """
#     # Load bank public key
#     with open(bank_public_key_path, "rb") as f:
#         key = jwk.JWK.from_pem(f.read())

#     # Prepare payload
#     payload_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

#     # Build JWE object
#     jwetoken = jwe.JWE(
#         plaintext=payload_json.encode("utf-8"),
#         protected={"alg": "RSA-OAEP", "enc": "A128CBC-HS256"}
#     )
#     jwetoken.add_recipient(key)

#     # Serialize compact format
#     return jwetoken.serialize(compact=True)


# # ---------------- CREATE VPA ----------------
# async def create_vpa(
#     access_token: str,
#     account_number: str = "60441010001739",
#     mobile_number: str = "9003088363",
#     name: str = "DynamicQrCode",
#     terminal_id: str = "TRDCIP0001",
#     bank_name: str = "Canara Bank",
#     ifsc_code: str = "CNRB0016044",
#     mid: str = "RNFMID0001",
#     mcc: str = "5411",
#     sid: str = "SIDCIP0001",
#     additional_no: str = " ",
# ) -> Dict:
#     """
#     Build payload, encrypt using JWE, sign, set headers, and call bank VPA API
#     """
#     encrypt_data = {
#         "mid": mid,
#         "channel": "api",
#         "account_number": str(account_number),
#         "mobile_number": str(mobile_number),
#         "terminalId": terminal_id,
#         "name": name,
#         "bank_name": bank_name,
#         "mcc": str(mcc),
#         "ifsc_code": ifsc_code,
#         "checksum": "",
#         "additionalNo": additional_no,
#         "sid": sid
#     }

#     # ---------------- ENCRYPT ----------------
#     encrypted_string = encrypt_jwe_aes_cbc_hs256(encrypt_data, PUBLIC_KEY)
#     print("encrypted_string: - vpa_service.py:106", encrypted_string)

#     # ---------------- PAYLOAD ----------------
#     payload = {
#         "Request": {
#             "body": {
#                 "encryptData": encrypted_string
#             }
#         }
#     }
#     print("payload: - vpa_service.py:116", payload)

#     # ---------------- SIGN ----------------
#     signature = sign_payload_rsa_sha256(payload, PRIVATE_KEY_PATH)
#     print("signature: - vpa_service.py:120", signature)

#     # ---------------- HEADERS ----------------
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "x-client-id": CLIENT_ID,
#         "x-client-secret": CLIENT_SECRET,
#         "x-client-certificate": PUBLIC_KEY,
#         "x-api-interaction-id": str(uuid.uuid4()),
#         "x-timestamp": datetime.utcnow().isoformat() + "Z",
#         "Content-Type": "application/json",
#         "x-signature": signature,
#         "x-forwarded-for": CLIENT_IP,
#         "Cookie": "anyvalue=1"
#     }

#     # ---------------- SEND REQUEST ----------------
#     async with httpx.AsyncClient(timeout=30, verify=True) as client:
#         response = await client.post(API_URL, headers=headers, json=payload)

#     # ---------------- HANDLE RESPONSE ----------------
#     try:
#         return response.json()
#     except json.JSONDecodeError:
#         return {"status_code": response.status_code, "text": response.text}
    



# ---------------- SIGNING ----------------
def sign_payload_rsa_sha256(payload: dict, private_key_path: Path) -> str:
    """
    Sign JSON payload using RSA-SHA256 and return Base64 signature
    """
    message = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode("utf-8")


# ---------------- JWE ENCRYPTION ----------------
def encrypt_jwe_aes_cbc_hs256(data: dict, bank_public_key_path: str) -> str:
    """
    Encrypt payload using AES-128-CBC + HMAC-SHA256 wrapped in JWE (RSA-OAEP)
    Returns compact JWE string
    """
    # Load Bank Public Key
    key = jwk.JWK.from_pem(Path(bank_public_key_path).read_bytes())

    # Prepare payload
    payload_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    # Build JWE object
    jwetoken = jwe.JWE(
        plaintext=payload_json.encode("utf-8"),
        protected={"alg": "RSA-OAEP", "enc": "A128CBC-HS256"}
    )
    jwetoken.add_recipient(key)

    # Serialize compact format
    return jwetoken.serialize(compact=True)


# ---------------- CREATE VPA ----------------
async def create_vpa(
    access_token: str,
    account_number: str = "60441010001739",
    mobile_number: str = "9003088363",
    name: str = "DynamicQrCode",
    terminal_id: str = "TRDCIP0001",
    bank_name: str = "Canara Bank",
    ifsc_code: str = "CNRB0016044",
    mid: str = "RNFMID0001",
    mcc: str = "5411",
    sid: str = "SIDCIP0001",
    additional_no: str = " ",
) -> Dict:
    """
    Build payload, encrypt using JWE, sign, set headers, and call bank VPA API
    """
    # ---------------- BUILD ENCRYPT DATA ----------------
    encrypt_data = {
        "mid": mid,
        "channel": "api",
        "account_number": str(account_number),
        "mobile_number": str(mobile_number),
        "terminalId": terminal_id,
        "name": name,
        "bank_name": bank_name,
        "mcc": str(mcc),
        "ifsc_code": ifsc_code,
        "checksum": "",
        "additionalNo": additional_no,
        "sid": sid
    }

    # ---------------- ENCRYPT PAYLOAD ----------------
    encrypted_string = encrypt_jwe_aes_cbc_hs256(encrypt_data, PUBLIC_KEY)

    # ---------------- FINAL PAYLOAD ----------------
    payload = {
        "Request": {
            "body": {
                "encryptData": encrypted_string
            }
        }
    }

    # ---------------- SIGN PAYLOAD ----------------
    signature = sign_payload_rsa_sha256(payload, PRIVATE_KEY_PATH)

    # ---------------- HEADERS ----------------
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-client-certificate": Path(PUBLIC_KEY).read_text(),  # PEM content
        "x-api-interaction-id": str(uuid.uuid4()),
        "x-timestamp": datetime.utcnow().isoformat() + "Z",
        "Content-Type": "application/json",
        "x-signature": signature,
        "x-forwarded-for": CLIENT_IP,
        "Cookie": "anyvalue=1"
    }

    # ---------------- SEND REQUEST ----------------
    async with httpx.AsyncClient(timeout=30, verify=True) as client:
        response = await client.post(API_URL, headers=headers, json=payload)

    # ---------------- HANDLE RESPONSE ----------------
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"status_code": response.status_code, "text": response.text}
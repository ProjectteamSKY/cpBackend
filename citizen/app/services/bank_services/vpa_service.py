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
import httpx
import random
import string

from jose import jwe
from jose.constants import ALGORITHMS
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


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

    # Private key without header/footer
    private_key_str = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCqmltBJslKy8d9jVcVznYvLN8PpM6l2WRH8avjVE020pBKCiwytSTbj0Qg3F+zzX81BS0LNeXd90jVklfCpZWgn9zBKdOgcAadfRbKoqcGiZeX7IPi0y3ab0pheQYjHawqu9CI305N5s4kYOIT+WTqOwUsZ8PW/bZ6CkrWjYzLHkllNWFVZCC6sR6UuWKDVNYWeT6gGtiyvirxSvvj16gs0/V7TS2p4CshK1GoMBUkOv8fwrsSyeDqDRd5p1uUjD5yvHpBxvQK6gsTijB5MMgCt5laexzfFXcBvAVM8tJzQLBIWe3t/yDeqpX6voYmX+Qjsa9vy83/ceeigW1P/SjJAgMBAAECggEABVOA2YmdtRaKfmm3e1n0OB65QkQfSUlYCpcpsK6QCfZfpIqC3NY2PDf4K0neBgXHVlv4dXyXCT7ZzAS/2/b7jL9Fu9UaHL/qmo4BdGcvRwwfV4U98wqsFSeU0nK3q/uwHvxsMzdV7g1jrnorP+7kRU8wgLVznuzR8dqMG0mVIledNjKc5/6XIq5cExb04X/tLDD8gU6Pw9lRSJAaNpzHn1qLM9F4WPr4i/KCrU9DlZ7b2k6dxBEPCYOqZl4wVCrzbHyuNzusRIkjgo5TBIi2dZy4qRkKpJIoLsHw0Hm7GNP9H/lHtqtQdAnCZFSvRB8CJLyG+jocqnRzDU1iRfk+RQKBgQDZRv+LJBa2YinQz1CyLTIHTNQR+iJe5lmPgydVmHe+BoimNpJO4Abl1SEO+bYheiIAKt9yRcP574XTRyFFcZdWN8yW56H1g+YfU1vG7ZATcJi/eVZAHw6u8CToe6S08ypVi6gYszA6vl03uF9XMk8soRzOB9HY5tNThUlg0k4o1QKBgQDJAeYl164UJgfzWP1D5Ro4x7YEERh0F3d/eJXIs4/IFYjUAgatT1Bmo7FZ0wXEzk8eCxGqD9ZqPGw4le0iVtRdpMWPhzsiMDwXK0PqKbORGLrV/z2heifALcNgEDpj/ETJ6VXZCgWWMeH4Af2l74675Uvb6j3+/vpC3df6C06JQKBgAuUmigrWz6LStlDQ3TLrd/vu1nd8BkIw/s/LUiFoNQy+vOI8xFbJWL4khN/QbLVFJzXrCMmDsTyfDp/jwlpfXxt6uycGejBB/HheoHGxagTl0CVUgCG5zxxtjXh6SxvzXDTybjPTCHFZaiDnilCmC+zwppElm2uF9NaxkdvzhSlAoGAKVp9qe1sf/KvEg6N1GkO8v2LYdzOhhvJ1S44YarkebJCZnNxp2UAHD4a/1vYGKs4zEsA+OxmVCDg0H5QgvD7W5AkhJ/0vWkJIKpAZIdTAf6pxzdL8L/t8sBn6JwpPqQBeepfJtKROL+9FSQvHzlqxp9Btwem4JXz5qcYQR/4Jg0CgYA53781wxlgA+uy91i7ThMq6T8HnLsdxkG8xvjGVllL+OdaM6h0bvenC4k79eCOkZLgii9sjkMUk42u8QVpMmDnrU9vlwZoCm+Nt7oFE6Y2+Sm5DIPCjbmP2Tbko5URQtVJGUUuHRHj1GurbY2meIgfFhO6VEEFedaO0y9mcvwszg=="  


    private_key_pem = f"""-----BEGIN PRIVATE KEY-----
{private_key_str}
-----END PRIVATE KEY-----""".encode()

    private_key = serialization.load_pem_private_key(
        private_key_pem,
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
        "sid": sid
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

    # ----------------------------
    # Digital Signature
    # ----------------------------

    signature = sign(payload_json)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-client-id": CLIENT_ID,
        "x-client-secret": CLIENT_SECRET,
        "x-client-certificate": PUBLIC_KEY,
        "x-api-interaction-id": "1",
        "x-timestamp": str(time.time()),
        "x-signature": signature,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(
            API_URL,
            data=payload_json,
            headers=headers
        )

    print("STATUS: - vpa_service.py:223", response.status_code)
    print("ENCRYPTED RESPONSE: - vpa_service.py:224", response.text)

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
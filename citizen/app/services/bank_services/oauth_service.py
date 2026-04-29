from datetime import datetime, timedelta, timezone

import httpx
import base64

from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

CLIENT_ID="HlpU92cKxh4Aq3wwOMttGsyKddgneAl2"
CLIENT_SECRET="vh8LSH58ZuVCFSNMcAnOxf9lpGth1aNg"
TOKEN_URL="https://api.canara.bank.in/v1/oauth2/token"
REFRESH_URL="https://api.canara.bank.in/v1/oauth2/refresh-token"
REDIRECT_URI="https://api.citizenprintz.in/api/bank/oauth-callback"
DEFAULT_SCOPE="collection"
# Temporary token storage
token_storage = {
    "access_token": None,
    "refresh_token": None
}


# def basic_auth():
#     credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
#     encoded = base64.b64encode(credentials.encode()).decode()
#     return f"Basic {encoded}"


# async def generate_access_token(code: str, scope: str = DEFAULT_SCOPE):
#     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ - oauth_service.py:31")

#     headers = {
#         "Authorization": basic_auth(),
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! - oauth_service.py:37")
#     payload = {
#         "grant_type": "authorization_code",
#         "code": code,
#         "redirect_uri": REDIRECT_URI,
#         "scope": scope
#     }

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.post(TOKEN_URL, headers=headers, data=payload)
#         print("response - oauth_service.py:47",response)

#     if response.status_code != 200:
#         raise Exception(f"Token API Error: {response.text}")
#     print("response - oauth_service.py:51",response.text)
#     token_data = response.json()

#     token_storage["access_token"] = token_data.get("access_token")
#     token_storage["refresh_token"] = token_data.get("refresh_token")

#     return token_data


# async def refresh_access_token(refresh_token: str):

#     headers = {
#         "Authorization": basic_auth(),
#         "Content-Type": "application/x-www-form-urlencoded"
#     }

#     payload = {
#         "grant_type": "refresh_token",
#         "refresh_token": refresh_token
#     }

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.post(REFRESH_URL, headers=headers, data=payload)

#     if response.status_code != 200:
#         raise Exception(f"Refresh Token API Error: {response.text}")

#     token_data = response.json()

#     token_storage["access_token"] = token_data.get("access_token")

#     return token_data


# def get_access_token():
#     print("token_storage - oauth_service.py:86")
#     return token_storage.get("access_token")


# def get_refresh_token():
#     return token_storage.get("refresh_token")

BANK_NAME = "canara"


def basic_auth():
    creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    return "Basic " + base64.b64encode(creds.encode()).decode()

def safe_int(value, default=0):
    if value in (None, "", "null"):
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# 🚀 GENERATE ACCESS TOKEN
async def generate_access_token(code: str, user_id: str):

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "collection"
    }

    headers = {
        "Authorization": basic_auth(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("TOKEN_URL: - oauth_service.py:124", TOKEN_URL)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            TOKEN_URL,
            data=payload,
            headers=headers
        )

    # 🔍 Debug logs
    print("TOKEN STATUS: - oauth_service.py:134", response.status_code)
    print("TOKEN RESPONSE: - oauth_service.py:135", response.text)

    if response.status_code != 200:
        raise Exception(f"Token Error: {response.text}")

    if not response.text.strip():
        raise Exception("Empty response from token API")

    try:
        data = response.json()
    except Exception:
        raise Exception(f"Invalid JSON response: {response.text}")

    print("PARSED TOKEN DATA: - oauth_service.py:148", data)

    # 💾 Save tokens with user_id
    await save_tokens(data, user_id)

    return data

# 💾 SAVE TOKENS (SAFE VERSION)
async def save_tokens(data: dict, user_id: str):

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")

    if not access_token:
        raise Exception("No access_token received")

    # ✅ Handle API inconsistencies
    expires_in = safe_int(data.get("expires_in"))
    refresh_expires_in = safe_int(
        data.get("refresh_token_expires_in") or data.get("refresh_expires_in")
    )

    # 🔍 Debug raw values
    print("expires_in raw: - oauth_service.py:171", repr(data.get("expires_in")))
    print("refresh_expires raw: - oauth_service.py:172", repr(data.get("refresh_token_expires_in")))
    print("refresh_expires alt: - oauth_service.py:173", repr(data.get("refresh_expires_in")))

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(seconds=expires_in)
    refresh_expires_at = now + timedelta(seconds=refresh_expires_in)

    print("expires_at: - oauth_service.py:180", expires_at)
    print("refresh_expires_at: - oauth_service.py:181", refresh_expires_at)

    await execute(
        queries["bank_oauth"]["upsert_tokens"],
        {
            "user_id": user_id,  # ✅ FIXED
            "bank_name": BANK_NAME,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "refresh_expires_at": refresh_expires_at
        }
    )

# ✅ REFRESH TOKEN
async def refresh_access_token():

    token = await query(
        queries["bank_oauth"]["get_tokens"],
        {"bank_name": BANK_NAME}
    )

    if not token:
        raise Exception("Token not found")

    user_id = token.get("user_id")   # ✅ get from DB

    if not user_id:
        raise Exception("user_id missing in DB")

    if not token.get("refresh_token"):
        raise Exception("No refresh token found")

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": token["refresh_token"]
    }

    headers = {
        "Authorization": basic_auth(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(REFRESH_URL, data=payload, headers=headers)

    print("REFRESH STATUS: - oauth_service.py:227", response.status_code)
    print("REFRESH RESPONSE: - oauth_service.py:228", response.text)

    if response.status_code != 200:
        raise Exception(f"Refresh Error: {response.text}")

    data = response.json()

    # ✅ reuse same user_id
    await save_tokens(data, user_id)

    return data.get("access_token")

def make_aware(dt) -> datetime:
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # ← key fix
    return dt

#  GET VALID TOKEN (Auto Refresh)
async def get_valid_access_token():

    token = await query(
        queries["bank_oauth"]["get_tokens"],
        {"bank_name": BANK_NAME}
    )

    if not token:
        raise Exception("Token not found")

    expires_at = make_aware(token.get("expires_at"))

    if not expires_at:
        raise Exception("Invalid token expiry")

    now = datetime.now(timezone.utc)

    # 🔄 Refresh if expired (with buffer)
    if expires_at <= now + timedelta(minutes=2):
        return await refresh_access_token()  # OK if single-user

    return token["access_token"]
import datetime

import httpx
import base64
# from app.core.config import (
#     CLIENT_ID,
#     CLIENT_SECRET,
#     TOKEN_URL,
#     REFRESH_URL,
#     REDIRECT_URI,
#     DEFAULT_SCOPE
# )
CLIENT_ID="AUx27zglhuuiRxahKUTmpAVEVKuJ3rsr"
CLIENT_SECRET="B7WgKfGeURXYkEgRA1ZASYRFtUG64SEn"
TOKEN_URL = "https://api.canarauat.bank.in/v1/oauth2/token"
REFRESH_URL = "https://api.canarauat.bank.in/v1/oauth2/refresh-token"

REDIRECT_URI = "http://54.206.3.97/api/bank/oauth-callback"
DEFAULT_SCOPE = "upi"

token_storage = {
    "access_token": None,
    "refresh_token": None,
    "access_expiry": None,
    "refresh_expiry": None
}


def basic_auth():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


async def generate_access_token(code: str, scope: str = DEFAULT_SCOPE):

    headers = {
        "Authorization": basic_auth(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": scope
    }

    print("TOKEN REQUEST PAYLOAD: - oauth_service.py:49", payload)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            TOKEN_URL,
            headers=headers,
            data=payload
        )

    print("TOKEN STATUS: - oauth_service.py:58", response.status_code)
    print("TOKEN RESPONSE: - oauth_service.py:59", response.text)

    if response.status_code != 200:
        raise Exception(response.text)

    token_data = response.json()

    now = datetime.datetime.utcnow()

    token_storage["access_token"] = token_data["access_token"]
    token_storage["refresh_token"] = token_data["refresh_token"]

    token_storage["access_expiry"] = now + datetime.timedelta(hours=24)
    token_storage["refresh_expiry"] = now + datetime.timedelta(days=7)

    return token_data
async def generate_access_token(code: str, scope: str = DEFAULT_SCOPE):

    headers = {
        "Authorization": basic_auth(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": scope
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            TOKEN_URL,
            headers=headers,
            data=payload
        )

    print("TOKEN STATUS: - oauth_service.py:96", response.status_code)
    print("TOKEN RESPONSE: - oauth_service.py:97", response.text)

    if response.status_code != 200:
        raise Exception(response.text)

    token_data = response.json()

    now = datetime.datetime.utcnow()

    token_storage["access_token"] = token_data["access_token"]
    token_storage["refresh_token"] = token_data["refresh_token"]

    token_storage["access_expiry"] = now + datetime.timedelta(hours=24)
    token_storage["refresh_expiry"] = now + datetime.timedelta(days=7)

    return token_data


async def refresh_access_token(refresh_token: str):

    headers = {
        "Authorization": basic_auth(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            REFRESH_URL,
            headers=headers,
            data=payload
        )

    if response.status_code != 200:
        raise Exception(response.text)

    token_data = response.json()

    now = datetime.datetime.utcnow()

    token_storage["access_token"] = token_data["access_token"]
    token_storage["refresh_token"] = token_data["refresh_token"]

    token_storage["access_expiry"] = now + datetime.timedelta(hours=24)
    token_storage["refresh_expiry"] = now + datetime.timedelta(days=7)

    return token_data


def get_tokens():
    return token_storage

async def get_valid_access_token():

    tokens = get_tokens()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    access_expiry = tokens.get("access_expiry")
    refresh_expiry = tokens.get("refresh_expiry")

    now = datetime.datetime.utcnow()

    # 1️⃣ Access token still valid
    if access_token and access_expiry and now < access_expiry:
        print("Using existing access token - oauth_service.py:167")
        return access_token

    # 2️⃣ Access expired → try refresh token
    if refresh_token and refresh_expiry and now < refresh_expiry:

        print("Access token expired. Refreshing... - oauth_service.py:173")

        token_data = await refresh_access_token(refresh_token)

        return token_data["access_token"]

    # 3️⃣ Refresh token expired
    raise Exception("Refresh token expired. OAuth authorization required again.")
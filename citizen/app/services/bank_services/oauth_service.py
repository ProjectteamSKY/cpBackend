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
TOKEN_URL="https://api.canarauat.bank.in /v1/oauth2/token"
REFRESH_URL="https://api.canarauat.bank.in/v1/oauth2/refresh-token"
REDIRECT_URI="http://54.206.3.97/api/bank/oauth-callback"
DEFAULT_SCOPE="van"
# Temporary token storage
token_storage = {
    "access_token": None,
    "refresh_token": None
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

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(TOKEN_URL, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Token API Error: {response.text}")

    token_data = response.json()

    token_storage["access_token"] = token_data.get("access_token")
    token_storage["refresh_token"] = token_data.get("refresh_token")

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
        response = await client.post(REFRESH_URL, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Refresh Token API Error: {response.text}")

    token_data = response.json()

    token_storage["access_token"] = token_data.get("access_token")

    return token_data


def get_access_token():
    return token_storage.get("access_token")


def get_refresh_token():
    return token_storage.get("refresh_token")
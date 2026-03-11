import httpx
from typing import Dict
from base64 import b64encode

CANARA_BASE_URL = "https://api.canarauat.bank.in/v1"
CLIENT_ID = "<YOUR_CLIENT_ID>"
CLIENT_SECRET = "<YOUR_CLIENT_SECRET>"
REDIRECT_URI = "<YOUR_REDIRECT_URI>"
SCOPE = "<YOUR_SCOPE>"

# Simple in-memory token storage
TOKEN_STORE = {
    "access_token": None,
    "refresh_token": None,
    "expires_in": None  # timestamp or seconds
}

def get_basic_auth_header() -> str:
    """
    Returns Basic Auth header
    """
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = b64encode(auth_str.encode()).decode()
    return f"Basic {b64_auth}"


async def generate_access_token(code: str) -> Dict:
    """
    Generate Access Token from authorization code
    """
    url = f"{CANARA_BASE_URL}/oauth2/token"
    headers = {
        "Authorization": get_basic_auth_header(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()

        # Save tokens in memory
        TOKEN_STORE["access_token"] = token_data.get("access_token")
        TOKEN_STORE["refresh_token"] = token_data.get("refresh_token")
        TOKEN_STORE["expires_in"] = token_data.get("expires_in")  # seconds

        return token_data


async def refresh_access_token(refresh_token: str) -> Dict:
    """
    Refresh Access Token using refresh token
    """
    url = f"{CANARA_BASE_URL}/oauth2/refresh-token"
    headers = {
        "Authorization": get_basic_auth_header(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()

        # Update token store
        TOKEN_STORE["access_token"] = token_data.get("access_token")
        TOKEN_STORE["refresh_token"] = token_data.get("refresh_token")
        TOKEN_STORE["expires_in"] = token_data.get("expires_in")

        return token_data


def get_saved_access_token() -> str:
    """
    Return saved access token
    """
    return TOKEN_STORE.get("access_token")
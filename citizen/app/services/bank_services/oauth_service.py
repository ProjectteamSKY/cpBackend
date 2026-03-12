import httpx
import base64

CANARA_BASE_URL = "https://api.canarauat.bank.in/v1"

CLIENT_ID = "<YOUR_CLIENT_ID>"
CLIENT_SECRET = "<YOUR_CLIENT_SECRET>"

REDIRECT_URI = "http://54.206.3.97/api/bank/oauth-callback"


# In-memory storage
token_storage = {
    "access_token": None,
    "refresh_token": None
}


def get_basic_auth():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


# ---------------------------------------
# Generate Access Token
# ---------------------------------------
async def generate_access_token(code: str, scope: str):

    url = f"{CANARA_BASE_URL}/oauth2/token"

    headers = {
        "Authorization": get_basic_auth(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "scope": scope
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=body)

    if response.status_code != 200:
        raise Exception(response.text)

    token_data = response.json()

    token_storage["access_token"] = token_data.get("access_token")
    token_storage["refresh_token"] = token_data.get("refresh_token")

    return token_data


# ---------------------------------------
# Refresh Access Token
# ---------------------------------------
async def refresh_access_token(refresh_token: str):

    url = f"{CANARA_BASE_URL}/oauth2/refresh-token"

    headers = {
        "Authorization": get_basic_auth(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=body)

    if response.status_code != 200:
        raise Exception(response.text)

    token_data = response.json()

    token_storage["access_token"] = token_data.get("access_token")

    return token_data


def get_saved_access_token():
    return token_storage.get("access_token")


def get_saved_refresh_token():
    return token_storage.get("refresh_token")
import json

import httpx
import random
import string
from app.services.bank_services.oauth_service import get_access_token

API_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation"

# Random alphanumeric generator
def generate_random_id(prefix="", length=6):
    chars = string.ascii_uppercase + string.digits
    return prefix + ''.join(random.choices(chars, k=length))

async def create_vpa(access_token: str):
    # Get OAuth access token
    if not access_token:
        raise ValueError("Access token is required")


    terminal_id = generate_random_id("TERM", 6)
    sid = generate_random_id("SID", 6)

    # Prepare request payload exactly as per API doc
    request_data = {
        "mid": "YOUTUBE001",
        "channel": "api",
        "account_number": "60441010001739",
        "mobile_number": "9003088363",
        "terminalId": terminal_id,
        "name": "citizenprints",
        "bank_name": "Canara Bank",
        "mcc": "5411",
        "ifsc_code": "CNRB0016044",
        "checksum": "",        # Bank handles checksum
        "additionalNo": "",    # Optional
        "sid": sid
    }

    payload = {
        "Request": {
            "body": {
                "encryptData": json.dumps(request_data)  # <-- JSON string
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(API_URL, json=payload, headers=headers)

        print("STATUS: - vpa_service.py:57", response.status_code)
        print("BANK RESPONSE: - vpa_service.py:58", response.text)

        # Try parsing JSON safely
        try:
            return response.json()
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response.text}")

    except Exception as e:
        raise Exception(f"VPA Creation Failed: {str(e)}")
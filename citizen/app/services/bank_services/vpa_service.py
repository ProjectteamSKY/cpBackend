import httpx
import uuid

API_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation"


async def create_vpa():

    encrypt_data = {
        "mid": "YOUTUBE001",
        "channel": "api",
        "account_number": "6025253000001",
        "mobile_number": "9885337002",
        "terminalId": "terma1",
        "name": "svra1",
        "bank_name": "Canara Bank",
        "mcc": "5411",
        "ifsc_code": "CNRB0000000",
        "checksum": "",
        "additionalNo": "",
        "sid": "sida1"
    }

    payload = {
        "Request": {
            "body": {
                "encryptData": encrypt_data
            }
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            API_URL,
            json=payload,
            headers=headers
        )

    return response.json()
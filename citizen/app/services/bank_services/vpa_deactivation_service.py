import httpx

CANARA_VPA_DEACTIVATE_URL = "https://api.canarauat.bank.in/v1/upi/vpa-deactivation"


async def vpa_deactivation(mid: str, terminalId: str, sid: str, upiId: str):

    payload = {
        "Request": {
            "body": {
                "encryptData": {
                    "channel": "api",
                    "upiId": upiId,
                    "mid": mid,
                    "terminalId": terminalId,
                    "sid": sid,
                    "checksum": ""
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(CANARA_VPA_DEACTIVATE_URL, json=payload)

    return response.json()
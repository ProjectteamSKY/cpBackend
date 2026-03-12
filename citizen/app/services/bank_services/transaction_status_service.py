import httpx

CANARA_TXN_STATUS_RRN_URL = "https://api.canarauat.bank.in/v1/upi/qrstatus-rrn"


async def transaction_status_rrn(rrn: str, terminalId: str, mid: str, sid: str):

    payload = {
        "Request": {
            "body": {
                "encryptData": {
                    "rrn": rrn,
                    "channel": "api",
                    "terminalId": terminalId,
                    "mid": mid,
                    "sid": sid,
                    "checksum": ""
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(CANARA_TXN_STATUS_RRN_URL, json=payload)

    return response.json()
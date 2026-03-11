import httpx

CANARA_TXN_STATUS_EXTID_URL = "https://api.canara.bank.in/v1/upi/qrstatus-extid"


async def transaction_status_extid(mid: str, terminalId: str, sid: str, extTransactionId: str):

    payload = {
        "Request": {
            "body": {
                "encryptData": {
                    "mid": mid,
                    "channel": "api",
                    "sid": sid,
                    "terminalId": terminalId,
                    "extTransactionId": extTransactionId,
                    "checksum": ""
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(CANARA_TXN_STATUS_EXTID_URL, json=payload)

    return response.json()
import httpx

CANARA_VERIFY_VPA_URL = "https://api.canarauat.bank.in/v1/upi/verify-vpa"


async def verify_vpa(source: str, channel: str, extTransactionId: str, upiId: str, terminalId: str, sid: str):

    payload = {
        "Request": {
            "body": {
                "encryptData": {
                    "source": source,
                    "channel": channel,
                    "extTransactionId": extTransactionId,
                    "upiId": upiId,
                    "terminalId": terminalId,
                    "sid": sid,
                    "checksum": ""
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(CANARA_VERIFY_VPA_URL, json=payload)

    return response.json()
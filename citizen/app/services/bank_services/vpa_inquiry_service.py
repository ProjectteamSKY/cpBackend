import httpx

CANARA_VPA_INQUIRY_URL = "https://api.canarauat.bank.in/v1/upi/vpa-creation-enq"


async def vpa_inquiry(mid: str, terminalId: str, sid: str, batch_id: str):

    payload = {
        "Request": {
            "body": {
                "encryptData": {
                    "channel": "api",
                    "mid": mid,
                    "terminalId": terminalId,
                    "sid": sid,
                    "batch_id": batch_id,
                    "checksum": ""
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(CANARA_VPA_INQUIRY_URL, json=payload)

    return response.json()
import httpx

CANARA_VPA_DEACTIVATION_ENQ_URL = "https://api.canarauat.bank.in/v1/upi/vpa-deactivation-enq"


async def vpa_deactivation_inquiry(mid: str, terminalId: str, sid: str, batch_id: str):

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
        response = await client.post(CANARA_VPA_DEACTIVATION_ENQ_URL, json=payload)

    return response.json()
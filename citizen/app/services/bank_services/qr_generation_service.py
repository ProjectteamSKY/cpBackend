import httpx

CANARA_QR_GENERATION_URL = "https://api.canarauat.bank.in/v1/upi/qr-generation"


async def generate_qr(
    amount: str,
    extTransactionId: str,
    remark: str,
    source: str,
    terminalId: str,
    sid: str,
    upiId: str,
    requestTime: str,
    receipt: str
):

    payload = {
        "Request": {
            "body": {
                "encryptData": {
                    "amount": amount,
                    "extTransactionId": extTransactionId,
                    "channel": "api",
                    "remark": remark,
                    "source": source,
                    "terminalId": terminalId,
                    "type": "D",
                    "param3": "param3",
                    "Param2": "param2",
                    "param1": "param1",
                    "sid": sid,
                    "upiId": upiId,
                    "requestTime": requestTime,
                    "reciept": receipt,
                    "checksum": ""
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(CANARA_QR_GENERATION_URL, json=payload)

    return response.json()
import httpx

CANARA_QR_STATEMENT_URL = "https://api.canarauat.bank.in/v1/upi/qrstmt"


async def get_qr_statement(
    mid: str,
    sid: str,
    terminalId: str,
    startDate: str,
    endDate: str,
    pageSize: str,
    pageNo: str
):

    payload = {
        "Request": {
            "body": {
                "encryptData": {
                    "mid": mid,
                    "sid": sid,
                    "terminalId": terminalId,
                    "startDate": startDate,
                    "endDate": endDate,
                    "pageSize": pageSize,
                    "pageNo": pageNo
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(CANARA_QR_STATEMENT_URL, json=payload)

    return response.json()
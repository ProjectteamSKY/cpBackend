from datetime import datetime, timedelta
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.bank_services.vpa_service import get_qr_statement

router = APIRouter()


# ✅ FORMAT OR DEFAULT FUNCTION
def format_or_default(date_str: str | None, is_start=True):
    now = datetime.now()

    try:
        if date_str and date_str.lower() != "string":
            parsed = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

            # 🔥 CRITICAL FIX → prevent future date
            if parsed > now:
                return now.strftime("%Y-%m-%d %H:%M:%S")

            return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass

    # 🔥 DEFAULT LOGIC
    if is_start:
        return (now - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    else:
        return now.strftime("%Y-%m-%d %H:%M:%S")  # ✅ NOT 23:59:59


# ✅ REQUEST MODEL
class QRStatementRequest(BaseModel):
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    pageSize: str = "5"
    pageNo: str = "0"
    access_token: str


# ✅ ROUTE
@router.post("/qr-statement")
async def qr_statement_route(payload: QRStatementRequest):

    # 🔥 FIX DATES HERE (IMPORTANT)
    start_date = format_or_default(payload.startDate, is_start=True)
    end_date = format_or_default(payload.endDate, is_start=False)

    print("FINAL DATES: - qr_statement_routes.py:51", start_date, end_date)

    response = await get_qr_statement(
        access_token=payload.access_token,
        start_date=start_date,
        end_date=end_date,
        page_size=payload.pageSize,
        page_no=payload.pageNo
    )

    return {
        "success": True,
        "data": response
    }
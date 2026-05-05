from fastapi import APIRouter, HTTPException, Request
from app.services.transaction_service import (
    get_transaction_by_ext_id,
    get_all_transactions,
    update_transaction_status
)
from sse_starlette.sse import EventSourceResponse
import asyncio
router = APIRouter()

# -----------------------------------
# Get by ext_transaction_id
# -----------------------------------
@router.get("/{ext_id}/stream")
async def stream_transaction_status(request: Request, ext_id: str):

    async def event_generator():
        while True:
            # stop if client disconnects
            if await request.is_disconnected():
                break

            data = await get_transaction_by_ext_id(ext_id)

            if not data:
                yield {
                    "event": "error",
                    "data": "Transaction not found"
                }
                break

            status = data.get("status")

            # ✅ Send current status once
            yield {
                "event": "completed" if status in ["SUCCESS", "FAILED"] else "status",
                "data": status
            }

            # ✅ Stop immediately if already final
            if status in ["SUCCESS", "FAILED"]:
                break

            await asyncio.sleep(3)

    return EventSourceResponse(event_generator())


# -----------------------------------
# Get all transactions
# -----------------------------------
@router.get("/")
async def get_all_transactions_endpoint():
    return await get_all_transactions()


# -----------------------------------
# Update status
# -----------------------------------
@router.put("/{ext_id}/status")
async def update_status_endpoint(ext_id: str, status: str):
    return await update_transaction_status(ext_id, status)
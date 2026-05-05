from fastapi import HTTPException
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_transaction(data: dict):
    """
    Create or update transaction (QR flow safe)
    """
    await execute(queries["transactions"]["create"], data)

    return await query(
        queries["transactions"]["get_by_ext_id"],
        {"ext_transaction_id": data["ext_transaction_id"]}
    )


# -------------------------
# GET ALL
# -------------------------
async def get_all_transactions():
    return await query_all(queries["transactions"]["get_all"])


# -------------------------
# GET BY EXT ID
# -------------------------
async def get_transaction_by_ext_id(ext_id: str):
    data = await query(
        queries["transactions"]["get_by_ext_id"],
        {"ext_transaction_id": ext_id}
    )

    return data


# -------------------------
# UPDATE QR
# -------------------------
async def update_transaction_qr(ext_id: str, qr_string: str):
    await execute(
        queries["transactions"]["update"],
        {
            "ext_transaction_id": ext_id,
            "qr_string": qr_string
        }
    )

    return await get_transaction_by_ext_id(ext_id)


# -------------------------
# UPDATE STATUS
# -------------------------
async def update_transaction_status(ext_id: str, status: str):
    await execute(
        queries["transactions"]["update_status"],
        {
            "ext_transaction_id": ext_id,
            "status": status
        }
    )

    return await get_transaction_by_ext_id(ext_id)


# -------------------------
# DELETE
# -------------------------
async def delete_transaction(ext_id: str):
    existing = await get_transaction_by_ext_id(ext_id)

    if not existing:
        return None

    await execute(
        queries["transactions"]["delete"],
        {"ext_transaction_id": ext_id}
    )

    return {"ext_transaction_id": ext_id}
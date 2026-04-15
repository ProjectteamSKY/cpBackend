# app/services/design_request_service.py

from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all
import uuid
from datetime import datetime

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_design_request(data: dict):
    data["id"] = str(uuid.uuid4())

    now = datetime.utcnow()
    data["created_at"] = now
    data["updated_at"] = now

    data.setdefault("status", "NEW")
    data.setdefault("is_approved", False)
    data.setdefault("design_price", 0.0)
    data.setdefault("designed_images", "[]")

    await execute(queries["design_request"]["create"], data)

    return await get_design_request_by_id(data["id"])


# -------------------------
# GET ALL
# -------------------------
async def get_all_design_requests():
    return await query_all(queries["design_request"]["get_all"])


# -------------------------
# GET BY ID
# -------------------------
async def get_design_request_by_id(id: str):
    return await query(queries["design_request"]["get_by_id"], {"id": id})


# -------------------------
# UPDATE
# -------------------------
async def update_design_request(id: str, updates: dict):
    if not updates:
        return await get_design_request_by_id(id)
    print("UPDATES RECEIVED: - design_request_service.py:51", updates)
    updates["updated_at"] = datetime.utcnow()

    allowed_fields = {
        "status",
        "is_approved",
        "designed_images",
        "logo_images",
        "design_price",
        "name",
        "phone",
        "email",
        "product_id",
        "product_name",
        "variant_id",
        "variant_price_id", 
        "design_notes",
        "updated_at"
    }

    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

    if not filtered_updates:
        return await get_design_request_by_id(id)

    set_clause = ", ".join([f"{key} = :{key}" for key in filtered_updates.keys()])
    sql = f"""
        UPDATE design_requests
        SET {set_clause}
        WHERE id = :id
    """
    await execute(sql, {"id": id, **filtered_updates})
    return await get_design_request_by_id(id)


# -------------------------
# DELETE
# -------------------------
async def delete_design_request(id: str):
    existing = await get_design_request_by_id(id)
    if not existing:
        return None

    await execute(queries["design_request"]["delete"], {"id": id})
    return {"id": id}

async def get_design_requests_by_user_id(user_id: str):
    return await query_all(
        queries["design_request"]["get_by_user"],
        {"user_id": user_id}
    )
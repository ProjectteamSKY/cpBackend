from datetime import datetime
import uuid
from app.domain.user_address_domain import UserAddress
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# CREATE
async def create_user_address(address: UserAddress):
    address.id = str(uuid.uuid4())
    address.created_at = datetime.utcnow()

    data = address.to_dict()

    # ensure default values
    data.setdefault("is_default", False)

    await execute(queries["user_address"]["create"], data)

    return await get_address_by_id(address.id)


# GET ALL
async def get_all_addresses(user_id: str):
    return await query_all(
        queries["user_address"]["get_all"],
        {"user_id": user_id}
    )


# GET BY ID
async def get_address_by_id(id: str):
    return await query(
        queries["user_address"]["get_by_id"],
        {"id": id}
    )


# UPDATE
async def update_user_address(id: str, updates: dict):
    set_clause = ", ".join([f"{key} = :{key}" for key in updates.keys()])

    await execute(
        queries["user_address"]["update"].format(set_clause=set_clause),
        {"id": id, **updates}
    )

    return await get_address_by_id(id)


# DELETE
async def delete_user_address(id: str):
    existing = await get_address_by_id(id)

    if not existing:
        return None

    await execute(
        queries["user_address"]["delete"],
        {"id": id}
    )

    return {"id": id}
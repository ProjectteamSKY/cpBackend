from app.domain.contact_request_domain import ContactRequest
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


async def create_contact_request(contact: ContactRequest):

    await execute(
        queries["contact_requests"]["create"],
        contact.to_dict()
    )

    return await get_contact_request_by_id(contact.id)


async def get_all_contact_requests():
    return await query_all(
        queries["contact_requests"]["get_all"]
    )


async def get_contact_request_by_id(id: str):
    return await query(
        queries["contact_requests"]["get_by_id"],
        {"id": id}
    )


async def update_contact_request(id: str, updates: dict):

    if not updates:
        return await get_contact_request_by_id(id)

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())

    sql = queries["contact_requests"]["update"].format(
        set_clause=set_clause
    )

    await execute(sql, {"id": id, **updates})

    return await get_contact_request_by_id(id)


async def delete_contact_request(id: str):

    await execute(
        queries["contact_requests"]["delete"],
        {"id": id}
    )

    return {"id": id}
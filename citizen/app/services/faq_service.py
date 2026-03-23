from fastapi import HTTPException
from app.domain.faq_domain import FAQ
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_faq(faq: FAQ):
    await execute(queries["faq"]["create"], faq.to_dict())
    return await get_faq_by_id(faq.id)


# -------------------------
# GET ALL
# -------------------------
async def get_all_faqs():
    return await query_all(queries["faq"]["get_all"])


# -------------------------
# GET BY ID
# -------------------------
async def get_faq_by_id(id: str):
    return await query(queries["faq"]["get_by_id"], {"id": id})


# -------------------------
# PRODUCT PAGE FAQs
# -------------------------
async def get_product_faqs(category_id: str, product_id: str):
    return await query_all(
        queries["faq"]["get_by_product"],
        {"category_id": category_id, "product_id": product_id}
    )


# -------------------------
# CATEGORY PAGE FAQs
# -------------------------
async def get_category_faqs(category_id: str):
    return await query_all(
        queries["faq"]["get_by_category"],
        {"category_id": category_id}
    )


# -------------------------
# UPDATE
# -------------------------
async def update_faq(id: str, updates: dict):
    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    sql = queries["faq"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_faq_by_id(id)


# -------------------------
# DELETE
# -------------------------
async def delete_faq(id: str):
    await execute(queries["faq"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE / DEACTIVATE
# -------------------------
async def activate_faq(id: str):
    await execute(queries["faq"]["activate"], {"id": id})
    return await get_faq_by_id(id)


async def deactivate_faq(id: str):
    await execute(queries["faq"]["deactivate"], {"id": id})
    return await get_faq_by_id(id)
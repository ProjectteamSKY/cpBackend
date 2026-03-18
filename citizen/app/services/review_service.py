from typing import Optional

from fastapi import HTTPException
from app.domain.review_domain import CustomerReview
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()

# -------------------------
# CREATE
# -------------------------
async def create_review(review: CustomerReview, check_user=True, check_product=True):
    """
    Create a review. Automatically fetch customer_name from user_id.
    """
    # Fetch user and validate
    if check_user:
        user_record = await query(
            "SELECT id, full_name FROM users WHERE id = :id AND is_active = TRUE",
            {"id": review.user_id}
        )
        if not user_record:
            raise HTTPException(status_code=400, detail="Invalid user_id")
        review.customer_name = user_record["full_name"]  # auto-fill customer_name

    # Validate product
    if check_product:
        product_exists = await query("SELECT id FROM products WHERE id = :id", {"id": review.product_id})
        if not product_exists:
            raise HTTPException(status_code=400, detail="Invalid product_id")

    # Insert review
    await execute(queries["review"]["create"], review.to_dict())
    created = await query(queries["review"]["get_by_id"], {"id": review.id})
    return created

# -------------------------
# GET ALL
# -------------------------
async def get_all_reviews():
    return await query_all(queries["review"]["get_all"])

# -------------------------
# GET BY ID
# -------------------------
async def get_review_by_id(id: str):
    return await query(queries["review"]["get_by_id"], {"id": id})

# -------------------------
# UPDATE
# -------------------------
async def update_review(id: str, updates: dict):
    if not updates:
        return await get_review_by_id(id)

    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["review"]["update"].format(set_clause=set_clause)
    await execute(sql, {"id": id, **updates})
    return await get_review_by_id(id)

# -------------------------
# SOFT DELETE
# -------------------------
async def delete_review(id: str):
    existing = await query(queries["review"]["get_by_id"], {"id": id})
    if not existing:
        return None
    await execute(queries["review"]["delete"], {"id": id})
    return {"id": id}

# -------------------------
# ACTIVATE / DEACTIVATE
# -------------------------
async def activate_review(id: str):
    await execute(queries["review"]["activate"], {"id": id})
    return await get_review_by_id(id)

async def deactivate_review(id: str):
    await execute(queries["review"]["deactivate"], {"id": id})
    return await get_review_by_id(id)

# -------------------------
# LAST 5 ACTIVE REVIEWS PER PRODUCT
# -------------------------
async def latest_reviews(product_id: str):
    return await query_all(queries["review"]["latest_per_product"], {"product_id": product_id})
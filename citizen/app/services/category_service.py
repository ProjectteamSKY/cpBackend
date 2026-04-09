from fastapi import HTTPException
from app.domain.category_domain import Category
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_category(category: Category):
    """
    Create a new category.
    If category exists and is active → raise error.
    If category exists but soft-deleted → reactivate it.
    Returns the created or reactivated category as dict.
    """
    existing = await query(
        "SELECT * FROM categories WHERE name = :name AND is_deleted = FALSE",
        {"name": category.name}
    )

    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")

    await execute(queries["category"]["create"], category.to_dict())
    created = await query(queries["category"]["get_by_id"], {"id": category.id})
    return created


# -------------------------
# GET ALL
# -------------------------
async def get_all_categories():
    """
    Fetch all categories as a list of dicts
    """
    return await query_all(queries["category"]["get_all"])


# -------------------------
# GET BY ID
# -------------------------
async def get_category_by_id(id: str):
    """
    Fetch a single category by ID
    """
    return await query(queries["category"]["get_by_id"], {"id": id})


# -------------------------
# UPDATE
# -------------------------
async def update_category(id: str, updates: dict):
    """
    Update category fields by ID
    """
    if not updates:
        return await get_category_by_id(id)

    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["category"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await get_category_by_id(id)


# -------------------------
# DELETE (soft delete)
# -------------------------
async def delete_category(id: str):
    # Check category exists
    existing = await query(queries["category"]["get_by_id"], {"id": id})
    if not existing:
        return None

    # ❌ Check subcategories
    subcategories = await query(
        queries["category"]["check_subcategories"], {"id": id}
    )
    if subcategories:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete: Category is assigned to subcategories"
        )

    # ❌ Check products
    products = await query(
        queries["category"]["check_products_by_category"], {"id": id}
    )
    if products:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete: Category is assigned to products"
        )

    # ✅ Safe to delete
    await execute(queries["category"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_category(id: str):
    """
    Activate a soft-deleted category
    """
    await execute(queries["category"]["activate"], {"id": id})
    return await get_category_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_category(id: str):
    """
    Deactivate a category
    """
    await execute(queries["category"]["deactivate"], {"id": id})
    return await get_category_by_id(id)
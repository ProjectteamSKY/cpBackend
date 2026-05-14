# app/services/subcategory_service.py

import json
from fastapi import HTTPException

from app.domain.subcategory_domain import Subcategory
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# 🔥 HELPER FUNCTIONS
# -------------------------

def serialize_images(images):
    """Convert Python list → JSON string for DB"""
    if isinstance(images, list):
        return json.dumps(images)
    return images


def deserialize_images(images):
    """Convert DB value → Python list safely"""
    if isinstance(images, str):
        try:
            return json.loads(images)
        except Exception:
            return []
    elif isinstance(images, list):
        return images
    return []


def attach_images(record: dict):
    """Ensure images field is always list"""
    if record and "images" in record:
        record["images"] = deserialize_images(record.get("images"))
    return record


# -------------------------
# CREATE
# -------------------------
async def create_subcategory(subcategory: Subcategory):

    existing = await query(
        "SELECT * FROM subcategories WHERE name = :name AND category_id = :category_id AND is_deleted = FALSE",
        {"name": subcategory.name, "category_id": subcategory.category_id}
    )

    if existing:
        raise HTTPException(status_code=400, detail="Subcategory already exists")

    data = subcategory.to_dict()

    # ✅ serialize images
    data["images"] = serialize_images(data.get("images", []))

    await execute(queries["subcategory"]["create"], data)

    created = await query(queries["subcategory"]["get_by_id"], {"id": subcategory.id})

    return attach_images(created)


# -------------------------
# GET ALL
# -------------------------
async def get_all_subcategories():
    data = await query_all(queries["subcategory"]["get_all"])

    return [attach_images(d) for d in data]


async def list_subcategory_base_products():
    data = await query_all(
        queries["subcategory"]["get_all_with_products"]
    )

    return [
        attach_images(dict(row))
        for row in data
    ]

# -------------------------
# GET ALL (MINIMAL)
# -------------------------
async def get_all_subcategories_minimal():
    data = await query_all(
        queries["subcategory"]["get_all_minimal"]
    )

    subcategories = []

    # return only first 8 VALID subcategories
    for sc in data:

        # attach image objects
        sc = attach_images(sc)

        images = sc.get("images", [])

        cleaned_images = []

        # validate images safely
        if isinstance(images, list):

            for img in images:

                if not isinstance(img, dict):
                    continue

                url = img.get("url")

                # skip empty/null urls
                if not url:
                    continue

                cleaned_images.append({
                    "id": img.get("id"),
                    "url": url,
                    "is_default": bool(
                        img.get("is_default", False)
                    )
                })

        # SKIP subcategory if no images
        if not cleaned_images:
            continue

        subcategories.append({
            "id": sc.get("id"),
            "name": sc.get("name"),
            "category_id": sc.get("category_id"),
            "category_name": sc.get("category_name"),
            "description": sc.get("description"),
            "is_active": bool(sc.get("is_active")),
            "images": cleaned_images[:8]
        })
        print(f"Processed subcategory {sc.get('id')} with {len(cleaned_images)} valid images - subcategory_service.py:142")
        # stop after 8 valid records
        if len(subcategories) >= 8:
            break

    return subcategories
# -------------------------
# GET BY ID
# -------------------------
async def get_subcategory_by_id(id: str):
    data = await query(queries["subcategory"]["get_by_id"], {"id": id})

    return attach_images(data)


# -------------------------
# GET BY CATEGORY
# -------------------------
async def get_subcategories_by_category(category_id: str):
    data = await query_all(
        queries["subcategory"]["get_by_category"],
        {"category_id": category_id}
    )

    return [attach_images(d) for d in data]


# -------------------------
# UPDATE
# -------------------------
async def update_subcategory(id: str, updates: dict):

    if not updates:
        return await get_subcategory_by_id(id)

    # ✅ serialize images safely
    if "images" in updates:
        updates["images"] = serialize_images(updates["images"])

    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    sql = queries["subcategory"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})

    result = await get_subcategory_by_id(id)

    return result


# -------------------------
# DELETE (soft delete)
# -------------------------
async def delete_subcategory(id: str):
    existing = await query(queries["subcategory"]["get_by_id"], {"id": id})
    if not existing:
        return None

    # ❌ Check products
    products = await query(
        queries["subcategory"]["check_products_by_subcategory"], {"id": id}
    )

    if products:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete: Subcategory is assigned to products"
        )

    # ✅ Safe delete
    await execute(queries["subcategory"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_subcategory(id: str):
    await execute(queries["subcategory"]["activate"], {"id": id})

    return await get_subcategory_by_id(id)


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_subcategory(id: str):
    await execute(queries["subcategory"]["deactivate"], {"id": id})

    return await get_subcategory_by_id(id)
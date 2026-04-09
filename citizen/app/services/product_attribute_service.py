from fastapi import HTTPException
from app.domain.product_attribute_domain import ProductAttribute
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_product_attribute(obj: ProductAttribute):

    existing = await query(
        """
        SELECT * FROM product_attributes
        WHERE product_id = :product_id
        AND attribute_id = :attribute_id
        AND is_deleted = FALSE
        """,
        {
            "product_id": obj.product_id,
            "attribute_id": obj.attribute_id
        }
    )

    if existing:
        raise HTTPException(status_code=400, detail="Attribute already assigned")

    await execute(queries["product_attributes"]["create"], obj.to_dict())
    return await query(queries["product_attributes"]["get_by_id"], {"id": obj.id})

async def get_all_product_attributes():
    return await query_all(
        queries["product_attributes"]["get_all"]
    )
# -------------------------
# GET BY PRODUCT
# -------------------------
async def get_product_attributes(product_id: str):
    return await query_all(
        queries["product_attributes"]["get_by_product"],
        {"product_id": product_id}
    )


# -------------------------
# UPDATE
# -------------------------
async def update_product_attribute(id: str, updates: dict):
    if not updates:
        return await query(queries["product_attributes"]["get_by_id"], {"id": id})

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    sql = queries["product_attributes"]["update"].format(set_clause=set_clause)

    await execute(sql, {"id": id, **updates})
    return await query(queries["product_attributes"]["get_by_id"], {"id": id})


# -------------------------
# DELETE
# -------------------------
async def delete_product_attribute(id: str):
    existing = await query(queries["product_attributes"]["get_by_id"], {"id": id})
    if not existing:
        return None

    await execute(queries["product_attributes"]["delete"], {"id": id})
    return {"id": id}


# -------------------------
# ACTIVATE
# -------------------------
async def activate_product_attribute(id: str):
    await execute(queries["product_attributes"]["activate"], {"id": id})
    return await query(queries["product_attributes"]["get_by_id"], {"id": id})


# -------------------------
# DEACTIVATE
# -------------------------
async def deactivate_product_attribute(id: str):
    await execute(queries["product_attributes"]["deactivate"], {"id": id})
    return await query(queries["product_attributes"]["get_by_id"], {"id": id})
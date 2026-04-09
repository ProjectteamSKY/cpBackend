from fastapi import HTTPException
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all
import uuid
from datetime import datetime

queries = load_queries()


async def create_multiple_variant_attribute_values(payload):
    results = []

    for value_id in payload.attribute_value_ids:

        # ✅ Validate attribute value
        value = await query(
            "SELECT * FROM attribute_values WHERE id = :id AND is_deleted = FALSE",
            {"id": value_id}
        )

        if not value:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid attribute value: {value_id}"
            )

        if value["attribute_id"] != payload.attribute_id:
            raise HTTPException(
                status_code=400,
                detail=f"Value {value_id} does not belong to attribute"
            )

        # ✅ Insert (no blocking for multi-values)
        obj = {
            "id": str(uuid.uuid4()),
            "variant_id": payload.variant_id,
            "attribute_id": payload.attribute_id,
            "attribute_value_id": value_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await execute(
            queries["variant_attribute_values"]["create"],
            obj
        )

        # ✅ Fetch inserted row
        row = await query(
            queries["variant_attribute_values"]["get_by_id"],
            {"id": obj["id"]}
        )

        if row:
            results.append(row)

    return results


async def get_values_by_variant(variant_id: str):
    return await query_all(
        queries["variant_attribute_values"]["get_by_variant"],
        {"variant_id": variant_id}
    )

async def update_variant_attribute_values(payload):
    results = []

    # --------------------------
    # Step 1: Validate all values
    # --------------------------
    for value_id in payload.attribute_value_ids:

        value = await query(
            "SELECT * FROM attribute_values WHERE id = :id AND is_deleted = FALSE",
            {"id": value_id}
        )

        if not value:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid attribute value: {value_id}"
            )

        if value["attribute_id"] != payload.attribute_id:
            raise HTTPException(
                status_code=400,
                detail=f"Value {value_id} does not belong to attribute"
            )

    # --------------------------
    # Step 2: Delete old values
    # --------------------------
    await execute(
        """
        DELETE FROM variant_attribute_values
        WHERE variant_id = :variant_id
        AND attribute_id = :attribute_id
        """,
        {
            "variant_id": payload.variant_id,
            "attribute_id": payload.attribute_id
        }
    )

    # --------------------------
    # Step 3: Insert new values
    # --------------------------
    for value_id in payload.attribute_value_ids:

        obj = {
            "id": str(uuid.uuid4()),
            "variant_id": payload.variant_id,
            "attribute_id": payload.attribute_id,
            "attribute_value_id": value_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await execute(
            queries["variant_attribute_values"]["create"],
            obj
        )

        row = await query(
            queries["variant_attribute_values"]["get_by_id"],
            {"id": obj["id"]}
        )

        if row:
            results.append(row)

    return results

async def delete_variant_attribute_value(id: str):
    existing = await query(
        queries["variant_attribute_values"]["get_by_id"],
        {"id": id}
    )

    if not existing:
        return None

    await execute(
        queries["variant_attribute_values"]["delete"],
        {"id": id}
    )

    return {"id": id}
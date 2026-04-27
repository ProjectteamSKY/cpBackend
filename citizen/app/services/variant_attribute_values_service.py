from fastapi import HTTPException
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all
import uuid
from datetime import datetime
from collections import defaultdict
import re


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


async def get_full_product_details(product_id: str):

    # -------------------------
    # 1. Get Variants
    # -------------------------
    variants = await query_all(
        """
        SELECT id
        FROM product_variant_combinations
        WHERE product_id = :product_id
        """,
        {"product_id": product_id}
    )

    if not variants:
        return {"product_id": product_id, "variants": []}

    variant_ids = [v["id"] for v in variants]

    # -------------------------
    # 2. SAFE IN clause
    # -------------------------
    placeholders = ",".join([f":id{i}" for i in range(len(variant_ids))])
    params = {f"id{i}": vid for i, vid in enumerate(variant_ids)}
    params["product_id"] = product_id

    # -------------------------
    # 3. Get Attributes
    # -------------------------
    attribute_rows = await query_all(f"""
        SELECT 
            pa.attribute_id,
            a.name AS attribute_name,
            pa.sort_order,
            vav.variant_id,
            vav.attribute_value_id,
            av.value AS attribute_value_name
        FROM product_attributes pa
        JOIN attributes a 
            ON pa.attribute_id = a.id

        LEFT JOIN variant_attribute_values vav
            ON vav.attribute_id = pa.attribute_id
            AND vav.variant_id IN ({placeholders})
            AND vav.is_deleted = FALSE

        LEFT JOIN attribute_values av 
            ON vav.attribute_value_id = av.id

        WHERE pa.product_id = :product_id
        AND pa.is_deleted = FALSE

        ORDER BY pa.sort_order ASC
    """, params)

    # -------------------------
    # 4. Get Prices (FIXED)
    # -------------------------
    price_rows = await query_all(f"""
        SELECT 
            id,
            variant_id,
            min_qty,
            max_qty,
            custom_qty,   
            price,
            weight,
            length,
            breadth,
            height,
            is_active
        FROM variant_prices
        WHERE variant_id IN ({placeholders})
        AND is_deleted = FALSE
        ORDER BY min_qty ASC
    """, params)

    # -------------------------
    # 5. Initialize Variant Map
    # -------------------------
    variant_map = {
        vid: {
            "variant_id": vid,
            "attributes": [],
            "prices": []
        }
        for vid in variant_ids
    }

    # -------------------------
    # 6. Group Attributes
    # -------------------------
    grouped_attrs = defaultdict(lambda: defaultdict(lambda: {
        "attribute_id": "",
        "attribute_name": "",
        "sort_order": 0,
        "values": []
    }))

    for row in attribute_rows:
        vid = row["variant_id"]

        if not vid:
            continue

        aid = row["attribute_id"]

        group = grouped_attrs[vid][aid]
        group["attribute_id"] = aid
        group["attribute_name"] = row["attribute_name"]
        group["sort_order"] = row["sort_order"]

        if row["attribute_value_id"]:
            group["values"].append({
                "attribute_value_id": row["attribute_value_id"],
                "attribute_value_name": row["attribute_value_name"]
            })

    # -------------------------
    # 7. Assign Attributes
    # -------------------------
    for vid, attrs in grouped_attrs.items():

        sorted_attrs = sorted(
            attrs.values(),
            key=lambda x: x["sort_order"]
        )

        for attr in sorted_attrs:
            attr.pop("sort_order", None)

        variant_map[vid]["attributes"] = sorted_attrs

    # -------------------------
    # 8. Map Prices 
    # -------------------------
    for row in price_rows:
        variant_map[row["variant_id"]]["prices"].append({
            "id": row["id"],
            "min_qty": row["min_qty"],
            "max_qty": row["max_qty"],
            "custom_qty": bool(row.get("custom_qty", False)),  
            "price": float(row["price"]),

            "weight": float(row.get("weight") or 0),
            "length": float(row.get("length") or 0),
            "breadth": float(row.get("breadth") or 0),
            "height": float(row.get("height") or 0),

            "is_active": bool(row.get("is_active", True))
        })

    # -------------------------
    # 9. Ensure ALL variants returned
    # -------------------------
    final_variants = list(variant_map.values())

    # -------------------------
    # 10. Final Response
    # -------------------------
    return {
        "product_id": product_id,
        "variants": final_variants
    }

def extract_number(value: str):
    """
    Extract first numeric value from any string.
    Examples:
        "200 gsm" → 200
        "300GSM" → 300
        "8.9 cm" → 8.9
        "Size 12.5" → 12.5
    """

    if value is None:
        return None

    match = re.search(r"\d+\.?\d*", str(value))
    
    if match:
        return float(match.group())

    return None


async def calculate_total_weight(variant_id: str, quantity: int):
    """
    Calculate total weight based on variant attributes and quantity
    """

    query = """
    SELECT 
        a.name AS attribute_name,
        av.value AS attribute_value
    FROM variant_attribute_values vav
    JOIN attributes a ON a.id = vav.attribute_id
    JOIN attribute_values av ON av.id = vav.attribute_value_id
    WHERE vav.variant_id = :variant_id
      AND vav.is_deleted = FALSE
    """

    rows = await query_all(query, {"variant_id": variant_id})

    width = None
    height = None
    gsm = None

    for r in rows:
        name = r["attribute_name"].lower()
        value = r["attribute_value"]

        if name == "width":
            width = extract_number(value)

        elif name == "height":
            height = extract_number(value)

        elif name == "gsm":
            gsm = extract_number(value)

    if not width or not height or not gsm:
        return {
            "error": "Missing width, height or gsm"
        }

    # cm → m conversion
    area_m2 = (width / 100) * (height / 100)

    weight_per_piece = area_m2 * gsm
    total_weight = weight_per_piece * quantity

    return {
        "variant_id": variant_id,
        "width_cm": width,
        "height_cm": height,
        "gsm": gsm,
        "quantity": quantity,
        "weight_per_piece_grams": round(weight_per_piece, 3),
        "total_weight_grams": round(total_weight, 3),
        "total_weight_kg": round(total_weight / 1000, 4)
    }
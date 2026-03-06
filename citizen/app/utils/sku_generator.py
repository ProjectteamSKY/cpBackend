import re
from app.core.database import query_all

async def generate_sku(product_name: str) -> str:
    # Step 1: slugify name
    prefix = re.sub(r'[^a-zA-Z0-9]+', '_', product_name.strip().lower())
    prefix = re.sub(r'_+', '_', prefix).strip('_')

    # Step 2: fetch existing SKUs with this prefix
    sql = "SELECT sku FROM products WHERE sku LIKE :prefix"
    rows = await query_all(sql, {"prefix": f"{prefix}%"})

    existing_numbers = []
    for row in rows:
        sku = row.get("sku")
        if sku and sku.startswith(prefix):
            parts = sku.split("_")
            if parts[-1].isdigit():
                existing_numbers.append(int(parts[-1]))

    # Step 3: generate next number
    next_number = 1
    if existing_numbers:
        next_number = max(existing_numbers) + 1

    sku = f"{prefix}_{next_number:03d}"  # e.g., visiting_card_001
    return sku
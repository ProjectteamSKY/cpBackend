import uuid
import asyncio
from datetime import datetime
from sqlalchemy import text

from database import get_session


card_sizes = [
    {"size": "86 x 54", "min_qty": 10, "Gloss/Matte": 20, "Silver": 25, "Gold": 25},
    {"size": "62 x 62", "min_qty": 12, "Gloss/Matte": 20, "Silver": 25, "Gold": 25},
    {"size": "70 x 100", "min_qty": 8, "Gloss/Matte": 30, "Silver": 32, "Gold": 32},
    {"size": "55 x 130", "min_qty": 6, "Gloss/Matte": 30, "Silver": 32, "Gold": 32},
    {"size": "75 x 110", "min_qty": 4, "Gloss/Matte": 35, "Silver": 37, "Gold": 37},
    {"size": "86 x 130", "min_qty": 4, "Gloss/Matte": 35, "Silver": 37, "Gold": 37},
]

papers = ["Gloss/Matte", "Silver", "Gold"]


async def seed():

    async for db in get_session():

        now = datetime.now()

        try:

            # CATEGORY
            category_id = str(uuid.uuid4())

            await db.execute(
                text("""
                INSERT INTO categories
                (id,name,description,is_active,is_deleted,created_at,updated_at)
                VALUES (:id,:name,:desc,TRUE,FALSE,:now,:now)
                """),
                {
                    "id": category_id,
                    "name": "ID Cards",
                    "desc": "Laminated & PVC ID cards",
                    "now": now
                }
            )

            # SUBCATEGORY
            subcategory_id = str(uuid.uuid4())

            await db.execute(
                text("""
                INSERT INTO subcategories
                (id,category_id,name,description,is_active,is_deleted,created_at,updated_at)
                VALUES (:id,:cat,:name,:desc,TRUE,FALSE,:now,:now)
                """),
                {
                    "id": subcategory_id,
                    "cat": category_id,
                    "name": "Laminated ID Cards",
                    "desc": "Double / Single Side",
                    "now": now
                }
            )

            # SIZES
            size_map = {}

            for row in card_sizes:

                width, height = row["size"].split(" x ")
                size_id = str(uuid.uuid4())

                await db.execute(
                    text("""
                    INSERT INTO sizes
                    (id,name,width,height,unit,is_active,is_deleted,created_at,updated_at)
                    VALUES (:id,:name,:w,:h,'mm',TRUE,FALSE,:now,:now)
                    """),
                    {
                        "id": size_id,
                        "name": row["size"],
                        "w": width,
                        "h": height,
                        "now": now
                    }
                )

                size_map[row["size"]] = size_id

            # PAPER TYPES
            paper_map = {}

            for paper in papers:

                paper_id = str(uuid.uuid4())

                await db.execute(
                    text("""
                    INSERT INTO paper_types
                    (id,name,description,is_active,is_deleted,created_at,updated_at)
                    VALUES (:id,:name,:desc,TRUE,FALSE,:now,:now)
                    """),
                    {
                        "id": paper_id,
                        "name": paper,
                        "desc": f"{paper} finish",
                        "now": now
                    }
                )

                paper_map[paper] = paper_id

            # PRINT TYPE
            print_id = str(uuid.uuid4())

            await db.execute(
                text("""
                INSERT INTO print_types
                (id,name,description,is_active,is_deleted,created_at,updated_at)
                VALUES (:id,'Standard Print','Standard Print',TRUE,FALSE,:now,:now)
                """),
                {"id": print_id, "now": now}
            )

            # CUT TYPE
            cut_id = str(uuid.uuid4())

            await db.execute(
                text("""
                INSERT INTO cut_types
                (id,name,description,is_active,is_deleted,created_at,updated_at)
                VALUES (:id,'Standard Cut','Standard Cut',TRUE,FALSE,:now,:now)
                """),
                {"id": cut_id, "now": now}
            )

            # PRODUCT
            product_id = str(uuid.uuid4())

            await db.execute(
                text("""
                INSERT INTO products
                (id,category_id,subcategory_id,name,description,sku,min_order_qty,max_order_qty,
                is_active,is_deleted,created_at,updated_at)
                VALUES (:id,:cat,:sub,'Laminated ID Cards','Laminated ID Cards','LIC001',1,1000,
                TRUE,FALSE,:now,:now)
                """),
                {
                    "id": product_id,
                    "cat": category_id,
                    "sub": subcategory_id,
                    "now": now
                }
            )

            # VARIANTS + PRICES
            for row in card_sizes:

                size_id = size_map[row["size"]]

                for paper in papers:

                    variant_id = str(uuid.uuid4())

                    await db.execute(
                        text("""
                        INSERT INTO product_variants
                        (id,product_id,size_id,paper_type_id,print_type_id,cut_type_id,
                        sides,two_side_cut,four_side_cut,orientation,
                        is_active,is_deleted,created_at,updated_at)
                        VALUES (:id,:product,:size,:paper,:print,:cut,
                        2,TRUE,FALSE,'Portrait',
                        TRUE,FALSE,:now,:now)
                        """),
                        {
                            "id": variant_id,
                            "product": product_id,
                            "size": size_id,
                            "paper": paper_map[paper],
                            "print": print_id,
                            "cut": cut_id,
                            "now": now
                        }
                    )

                    price_id = str(uuid.uuid4())

                    await db.execute(
                        text("""
                        INSERT INTO product_variant_prices
                        (id,variant_id,min_qty,price,is_active,is_deleted,created_at,updated_at)
                        VALUES (:id,:variant,:qty,:price,TRUE,FALSE,:now,:now)
                        """),
                        {
                            "id": price_id,
                            "variant": variant_id,
                            "qty": row["min_qty"],
                            "price": row[paper],
                            "now": now
                        }
                    )

            await db.commit()

            print("✅ Data inserted successfully")

        except Exception as e:
            await db.rollback()
            print("❌ Error:", e)


if __name__ == "__main__":
    asyncio.run(seed())
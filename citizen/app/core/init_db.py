# import asyncio
# from app.core.database import engine
# from app.db.models.user_model import (
#     Base,
#     User,
#     UserProfile,
#     UserToken,
#     Role,
#     Resource,
#     Permission,
#     UserRole,
#     RolePermission
# )
# from app.db.models.product_models import (
#     Category,
#     SubCategory,
#     ProductType,
#     PaperType,
#     Finish,
#     CutType,
#     Product,
#     ProductVariant,
#     ProductImage,
#     SheetTemplate,
# )

# from app.db.models.discounts_models import (
#    Discount
# )

# from app.db.models.order_models import (
#     OrderAddress,              
#     Order,                    
#     OrderItem,                 
#     ShipRocketAuth,            
#     ShipRocketPickupLocation, 
#     ShipRocketCourier,        
#     ShipRocketCourierRate,     
#     ShipRocketServiceability,  
#     ShipRocketOrder,           
#     ShipRocketShipment,        
#     ShipRocketInvoice,         
#     ShipRocketLabel,           
#     ShipRocketManifest,        
#     ShipRocketTracking,        
#     ShipRocketNDR,             
#     ShipRocketReturn,          
#     ShipRocketCODSettlement    
# )

# from app.db.models.order_files_models import (
#     OrderFile,                
# )

# from app.db.models.payments_models import (
#     Payment,
#     Refund,
#     PaymentMethod,
#     BankAccount,
#     Payout
# )


# from app.db.models.invoice_models import (
#    Invoice
# )

# from app.db.models.wishlist_model import (
#    Wishlist
# )

# async def init_db():
#     async with engine.begin() as conn:
#         print("Creating tables... - init_db.py:74")

#         # Run sync create_all inside async connection
#         #  Order matters due to foreign keys:
#         # 1. Users first
#         # 2. Roles and permissions
#         # 3. Products, categories, subcategories, variants, images
#         await conn.run_sync(Base.metadata.create_all)

#         print("All tables created successfully! - init_db.py:83")

# if __name__ == "__main__":
#     asyncio.run(init_db())


import os
import asyncio
from sqlalchemy import text
from app.core.database import engine

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "schema")

# ✅ Explicit execution order to respect foreign key dependencies
SQL_FILES_ORDER = [
    # "user.sql",
    # "product.sql",
    # "order.sql",
    # "user_order_file.sql",
    # "wish_list.sql",
    "cart.sql",
]


async def init_db():
    print("🚀 Initializing database... - init_db.py:108")

    async with engine.begin() as conn:  # ✅ Correct way
        for file in SQL_FILES_ORDER:

            path = os.path.join(SCHEMA_PATH, file)

            if not os.path.exists(path):
                print(f"⚠️ File not found: {file} - init_db.py:116")
                continue

            print(f"📄 Applying schema: {file} - init_db.py:119")

            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()

            # Split and execute each statement safely
            statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]

            for stmt in statements:
                await conn.execute(text(stmt))

    print("✅ All tables created successfully. - init_db.py:130")


if __name__ == "__main__":
    asyncio.run(init_db())
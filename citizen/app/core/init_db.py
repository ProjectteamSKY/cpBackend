import asyncio
from app.core.database import engine
from app.db.models.user_model import (
    Base,
    User,
    UserProfile,
    Role,
    UserRole,
    UserToken,
)
from app.db.models.product_models import (
    Category,
    SubCategory,
    ProductType,
    PaperType,
    Finish,
    CutType,
    Product,
    ProductVariant,
    ProductImage,
    SheetTemplate,
)

async def init_db():
    async with engine.begin() as conn:
        print("Creating tables... - init_db.py:26")

        # Run sync create_all inside async connection
        #  Order matters due to foreign keys:
        # 1. Users first
        # 2. Roles and permissions
        # 3. Products, categories, subcategories, variants, images
        await conn.run_sync(Base.metadata.create_all)

        print("All tables created successfully! - init_db.py:35")

if __name__ == "__main__":
    asyncio.run(init_db())

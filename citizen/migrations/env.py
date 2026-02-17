# migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from app.core.database import Base, DATABASE_URL

# Import all models here so Alembic knows about them
# ------------------------
# User & RBAC
# ------------------------
from app.db.models.user_model import (
    User,
    UserProfile,
    UserToken,
    Role,
    Resource,
    Permission,
    UserRole,
    RolePermission
)

# ------------------------
# Products & Catalog
# ------------------------
from app.db.models.product_models import (
    Category,
    SubCategory,
    ProductType,
    PaperType,
    Finish,
    Product,
    ProductImage,
    CutType,
    ProductVariant,
    ProductImage,
    SheetTemplate
)

# ------------------------
# Orders & Order Details
# ------------------------
# from app.db.models.orders_models import (
#     OrderAddress,
#     Order,
#     OrderItem
# )
# from app.db.models.order_files_models import OrderFile  # uploaded files for orders

# ------------------------
# Payments
# ------------------------
# from app.db.models.payments_models import Payment

# ------------------------
# Shipments
# ------------------------
# from app.db.models.shipment_models import Shipment

# ------------------------
# Invoices
# ------------------------
# from app.db.models.invoice_models import Invoice

# ------------------------
# Discounts & Promotions
# ------------------------
# from app.db.models.discounts_models import Discount

# ------------------------
# Wishlist
# ------------------------
# from app.db.models.wishlist_model import Wishlist

# ... add other tables as needed

# Alembic Config object
config = context.config

# Logging setup
fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

# ------------------------
# Offline mode
# ------------------------
def run_migrations_offline():
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------
# Online mode
# ------------------------
def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

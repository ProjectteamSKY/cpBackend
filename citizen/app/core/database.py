# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5432/citizenprints"

# 1. Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# 2. Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Declarative Base for ORM
class Base(DeclarativeBase):
    pass

# 4. Dependency for FastAPI routes
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

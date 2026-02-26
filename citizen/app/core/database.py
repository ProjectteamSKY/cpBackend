# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Make sure DATABASE_URL is correct (remove extra quote)
# DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5432/citizenprints"
# DATABASE_URL = "mysql+asyncmy://root:Password%40123@localhost:3306/citizenprints" // local env
# Live env
DATABASE_URL = "mysql+asyncmy://citizen_user:citizen%40123@localhost:3306/citizenprints" 


# 1. Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# 2. Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Declarative Base for ORM models
class Base(DeclarativeBase):
    pass

# 4. Dependency for FastAPI routes
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

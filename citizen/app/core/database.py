# # app/core/database.py
# import os

# from dotenv import load_dotenv
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, DeclarativeBase
# from sqlalchemy import MetaData
# load_dotenv()

# # Make sure DATABASE_URL is correct (remove extra quote)
# # DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5432/citizenprints"


# DATABASE_URL = os.getenv("DATABASE_URL")


# # 1. Async engine
# engine = create_async_engine(DATABASE_URL, echo=True)

# # 2. Async session factory
# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

# # 3. Declarative Base for ORM models
# class Base(DeclarativeBase):
#     pass



# SessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

# metadata = MetaData()

# # ======================
# # Async session dependency for FastAPI
# # ======================
# async def get_session():
#     async with SessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()

# # ======================
# # Optional raw connection
# # ======================
# async def get_connection():
#     async with engine.connect() as conn:
#         yield conn

# app/core/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import MetaData, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# -------------------------
# 1. Async engine
# -------------------------
engine = create_async_engine(DATABASE_URL, echo=True)

# -------------------------
# 2. Async session factory
# -------------------------
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# -------------------------
# 3. Declarative Base for ORM models
# -------------------------
class Base(DeclarativeBase):
    pass

metadata = MetaData()

# -------------------------
# Async session dependency for FastAPI
# -------------------------
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# -------------------------
# Optional raw connection
# -------------------------
async def get_connection():
    async with engine.connect() as conn:
        yield conn

# -------------------------
# Helper functions
# -------------------------

async def execute(sql: str, params: dict = {}):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    Returns None (or optionally affected row count).
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql), params)
        await session.commit()
        # Don't call fetchone() for non-SELECT queries
        return result.rowcount  # optional: number of affected rows

async def query(sql: str, params: dict = {}):
    """
    Execute a SELECT query and return the first row as a dict.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql), params)
        row = result.fetchone()
        return dict(row._mapping) if row else None

async def query_all(sql: str, params: dict = {}):
    """
    Execute a SELECT query and return all rows as list of dicts.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql), params)
        rows = result.fetchall()
        return [dict(r._mapping) for r in rows]

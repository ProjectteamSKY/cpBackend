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
# import os
# from dotenv import load_dotenv
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, DeclarativeBase
# from sqlalchemy import text

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise ValueError("DATABASE_URL is not set")


# # -------------------------
# # Engine
# # -------------------------
# engine = create_async_engine(DATABASE_URL, echo=True)

# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )


# class Base(DeclarativeBase):
#     pass


# # -------------------------
# # Dependency
# # -------------------------
# async def get_session():
#     async with AsyncSessionLocal() as session:
#         yield session


# # -------------------------
# # Helpers
# # -------------------------
# async def execute(sql: str, params: dict = {}):
#     async with AsyncSessionLocal() as session:
#         result = await session.execute(text(sql), params)
#         await session.commit()
#         return result.rowcount


# async def query(sql: str, params: dict = {}):
#     async with AsyncSessionLocal() as session:
#         result = await session.execute(text(sql), params)
#         row = result.fetchone()
#         return dict(row._mapping) if row else None


# async def query_all(sql: str, params: dict = {}):
#     async with AsyncSessionLocal() as session:
#         result = await session.execute(text(sql), params)
#         rows = result.fetchall()
#         return [dict(r._mapping) for r in rows]


import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


# -------------------------
# Engine (Optimized)
# -------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 🔁 set False in production
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)


# -------------------------
# Session Factory
# -------------------------
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# -------------------------
# Base Model
# -------------------------
class Base(DeclarativeBase):
    pass


# -------------------------
# Dependency (FastAPI)
# -------------------------
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# -------------------------
# Core Helpers
# -------------------------

async def execute(sql: str, params: dict = {}):
    """
    For INSERT / UPDATE / DELETE
    """
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text(sql), params)
            await session.commit()
            return result.rowcount
        except Exception as e:
            await session.rollback()
            raise e


async def execute_returning(sql: str, params: dict = {}):
    """
    Insert + return inserted row (if DB supports)
    """
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text(sql), params)
            await session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
        except Exception as e:
            await session.rollback()
            raise e


async def query(sql: str, params: dict = {}):
    """
    Fetch single row
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql), params)
        row = result.fetchone()
        return dict(row._mapping) if row else None


async def query_all(sql: str, params: dict = {}):
    """
    Fetch multiple rows
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql), params)
        rows = result.fetchall()
        return [dict(r._mapping) for r in rows]


async def scalar(sql: str, params: dict = {}):
    """
    Fetch single scalar value
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql), params)
        return result.scalar()


# -------------------------
# Transaction Helper
# -------------------------
async def run_in_transaction(func):
    """
    Run multiple DB operations safely in one transaction
    """

    async with AsyncSessionLocal() as session:
        try:
            result = await func(session)
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            raise e


# -------------------------
# Health Check (useful)
# -------------------------
async def check_db():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
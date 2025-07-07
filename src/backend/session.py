# src/backend/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager # Important for async dependencies
from typing import AsyncIterator

# Assuming config.py and database.dsn are set up for postgresql+asyncpg
from src.backend.config import config # Assuming config.py exists and has DSN

# Ensure your DSN uses postgresql+asyncpg
# Example: postgresql+asyncpg://user:pass@host:port/dbname
engine = create_async_engine(config.database.dsn)

# Use AsyncSession from sqlalchemy.ext.asyncio
AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession, # Specify AsyncSession here
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# This is your async dependency for FastAPI
async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback() # Use await for async rollback
            raise
        finally:
            await session.close() # Use await for async close

# You generally won't need an explicit 'open_session' context manager
# if you're using 'get_async_session' as a FastAPI dependency directly.
# If you need it for other async tasks, it would look like this:
@asynccontextmanager
async def open_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager


from src.backend.config import config

# 1) create engine
engine = create_async_engine(config.database.dsn)

# 2) create session factory

AsyncSessionFactory = sessionmaker(
    bind=engine,
    autoflush=False,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False
)

async def get_async_session()-> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def open_async_session()->AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close
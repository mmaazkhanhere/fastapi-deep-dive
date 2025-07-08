# crucial for managing async database sessions in FastAPI using SQLALchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager 
from typing import AsyncIterator


from src.backend.config import config 


engine = create_async_engine(config.database.dsn) #initialize async SQLAlchemy engine and is responsible for interacting with the database


AsyncSessionFactory = sessionmaker(
    bind=engine, #bind session factory to the engine. Any sessions created by AsyncSessionFactory will use this engine to connect with the database
    class_=AsyncSession, 
    autoflush=False, #transactions are not automatically committed and you need to explicitly call session.commit()
    expire_on_commit=False,
)


async def get_async_session() -> AsyncIterator[AsyncSession]: #async generator function designed to be used as FastAPI dependency
    async with AsyncSessionFactory() as session: #create a new AsyncSession and enters its async context
        try:
            yield session #perform database operation using session
        except Exception:
            await session.rollback() # if any error occurs, rollback the transaction
            raise
        finally:
            await session.close() # close the database connection regardless if exception is raised


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
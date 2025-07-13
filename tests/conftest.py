# tests/conftest.py

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool # Use NullPool for in-memory SQLite to prevent issues

from src.main import app
from src.backend.session import get_async_session
from src.db.database import Base

# --- Test Database Configuration ---
# Use an in-memory SQLite database for fast, isolated tests.
# This ensures each test starts with a clean slate.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create a test engine with NullPool for in-memory SQLite
# NullPool is important for in-memory SQLite to ensure each session gets a fresh connection
# and the database isn't shared across concurrent tests in a way that causes conflicts.
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False, # Set to True to see SQL queries during tests
    poolclass=NullPool,
    connect_args={"check_same_thread": False}, # Required for SQLite with FastAPI
)

# Create a sessionmaker for the test database
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False # Important for keeping objects accessible after commit in tests
)

# --- Dependency Override for Database Session ---
@pytest.fixture(name="session")
async def session_fixture():
    """
    Provides an isolated, asynchronous database session for each test.
    Ensures a clean database state before and after each test.
    """
    async with test_engine.begin() as conn:
        # Drop all tables and then create them for a clean slate
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Yield a new session for the test
    async with TestingSessionLocal() as session:
        yield session

    # After the test, drop all tables again to ensure isolation
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# --- Override FastAPI's get_async_session dependency ---
@pytest.fixture(name="override_get_async_session")
async def override_get_async_session_fixture(session: AsyncSession):
    """
    Fixture to override the get_async_session dependency in FastAPI.
    It yields the test session created by the 'session' fixture.
    """
    yield session

# --- FastAPI Test Client Fixture ---
@pytest.fixture(name="client")
async def client_fixture(override_get_async_session: AsyncSession):
    """
    Provides an asynchronous test client for the FastAPI application.
    Overrides the database dependency to use the test database.
    """
    # Override the get_async_session dependency
    app.dependency_overrides[get_async_session] = lambda: override_get_async_session

    # Use AsyncClient for testing async FastAPI applications
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clean up dependency overrides after the test
    app.dependency_overrides.clear()

    # Note on FastAPICache:
    # The 'lifespan' event in main.py will still attempt to initialize FastAPICache
    # with a real Redis connection. For true unit tests that don't rely on Redis,
    # you would typically mock or disable FastAPICache initialization during tests.
    # For integration tests where Redis is running, this setup is generally fine.
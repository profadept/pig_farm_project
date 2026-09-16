import os

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.main import app

load_dotenv()


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_session):
    app.dependency_overrides[get_session] = lambda: test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

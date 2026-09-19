import os

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.main import app
from src.models.user import User, UserRole
from src.security import hash_password

load_dotenv()


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    async with test_engine.connect() as connection, connection.begin():
        session = AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint"
        )
        yield session
        await connection.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_session):
    app.dependency_overrides[get_session] = lambda: test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(test_session):

    new_user = User(
        username="test_user",
        email="test_user123@gmail.com",
        hashed_password=hash_password("password12345"),
        full_name="Testin Name",
        role=UserRole.ADMIN,
        is_active=True,
    )

    test_session.add(new_user)
    await test_session.flush()

    yield


@pytest_asyncio.fixture(scope="function")
async def test_login(client, test_user):
    login_response = await client.post(
        "/login", data={"username": "test_user", "password": "password12345"}
    )

    assert login_response.status_code == 303
    yield client

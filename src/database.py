import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://farm_user:farm_password@db:5432/pig_farm_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session

import asyncio
import os

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import engine
from src.models import User, UserRole
from src.security import hash_password


async def create_initial_admin():
    async with AsyncSession(engine) as session:
        username = os.getenv("ADMIN_USERNAME")
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print(f"User '{username}' already exists in the vault!")
            return

        raw_password = os.getenv("ADMIN_PASSWORD")
        hashed_pw = hash_password(raw_password)

        new_admin = User(
            username=username,
            email=os.getenv("ADMIN_EMAIL"),
            hashed_password=hashed_pw,
            full_name=os.getenv("ADMIN_FULL_NAME"),
            role=UserRole.ADMIN,
            is_active=True,
        )

        session.add(new_admin)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(create_initial_admin())

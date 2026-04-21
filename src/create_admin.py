from sqlmodel import Session, select
from src.database import engine
from src.models import User, UserRole
from src.security import hash_password
import os


def create_initial_admin():
    with Session(engine) as session:
        username = os.getenv("ADMIN_USERNAME")
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()

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
        session.commit()


if __name__ == "__main__":
    create_initial_admin()

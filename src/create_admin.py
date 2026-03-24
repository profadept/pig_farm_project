from sqlmodel import Session, select
from src.database import engine
from src.models import User, UserRole
from src.security import hash_password


def create_initial_admin():
    with Session(engine) as session:
        # 1. Define the ONE username you want to use
        username = "profadept"

        print(f"Checking if {username} exists...")

        # 2. Check for THAT specific username
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()

        if existing_user:
            print(f"User '{username}' already exists in the vault!")
            return

        # 3. If not found, proceed to create
        raw_password = "FarmPassword2026"
        hashed_pw = hash_password(raw_password)

        new_admin = User(
            username=username,
            email="admin@yourfarm.com",
            hashed_password=hashed_pw,
            full_name="Farm SuperUser",
            role=UserRole.ADMIN,
            is_active=True,
        )

        session.add(new_admin)
        session.commit()
        print("✅ SUCCESS: Your Admin account has been created.")


if __name__ == "__main__":
    create_initial_admin()

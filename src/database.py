import os
from sqlmodel import create_engine, SQLModel


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://farm_user:farm_password@db:5432/pig_farm_db"
)

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

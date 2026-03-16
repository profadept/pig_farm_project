import os
from sqlmodel import create_engine, SQLModel

# 1. Grab the connection string from the environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://farm_user:farm_password@db:5432/pig_farm_db"
)

# 2. Create the Engine (The Translator/Wire)
engine = create_engine(DATABASE_URL, echo=True)


# 3. The Activation Switch
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

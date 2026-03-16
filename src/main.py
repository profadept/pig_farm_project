from fastapi import FastAPI
from contextlib import asynccontextmanager


from src.database import create_db_and_tables
from src import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the Pig Farm Database....")
    create_db_and_tables
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello and welcome to my pig farm project"}

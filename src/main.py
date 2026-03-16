from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from src.database import engine
from src.models import Transaction

# The Boss: Now with professional metadata for your documentation
app = FastAPI(
    title="Pig Farm Accounting API",
    description="A professional REST API for managing farm transactions and ledger entries.",
    version="0.1.0",
)


def get_session():
    """
    Dependency generator to manage database sessions.

    Yields a secure SQLAlchemy session for the current web request,
    and automatically closes the connection when the request is finished.
    """
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    """
    Health check endpoint.

    Returns a simple JSON greeting to verify the web server is awake and routing traffic.
    """
    return {"message": "Hello and welcome to my Pig Farm Website"}


@app.post("/transactions/", response_model=Transaction)
def create_transaction(
    transaction: Transaction, session: Session = Depends(get_session)
):
    """
    Create a new financial transaction in the Postgres ledger.

    Expects a complete Transaction JSON object in the request body.
    Fields marked as Optional in the SQLModel (like 'id' and 'remarks') can be omitted.

    Returns the newly created database record, complete with its auto-generated Postgres ID.
    """
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@app.get("/transactions/", response_model=list[Transaction])
def read_transactions():
    # 1. Open a "Session" (A temporary conversation with the DB)
    with Session(engine) as session:
        # 2. Write the Python version of "SELECT * FROM transaction"
        statement = select(Transaction)

        # 3. Execute the statement and grab the results
        results = session.exec(statement).all()

        # 4. Hand the list back to the browser
        return results

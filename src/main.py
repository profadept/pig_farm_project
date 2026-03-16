from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import date


from src.database import engine
from src.models import Transaction


# The Boss: Now with professional metadata for your documentation
app = FastAPI(
    title="Pig Farm Accounting API",
    description="A professional REST API for managing farm transactions and ledger entries.",
    version="0.1.0",
)

# Declare folders for FastAPI to check
templates = Jinja2Templates(directory="templates")


def get_session():
    """
    Dependency generator to manage database sessions.

    Yields a secure SQLAlchemy session for the current web request,
    and automatically closes the connection when the request is finished.
    """
    with Session(engine) as session:
        yield session


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Session = Depends(get_session)):
    """
    Main Dashboard Endpoint.

    Queries the database for all transaction records and injects them into 
    the index.html template using Jinja2 to render the visual ledger.
    """
    # 1. Grab all transactions using your secure session
    statement = select(Transaction)
    transactions = session.exec(statement).all()

    # 2. Hand the web request and the data over to the HTML template
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "transactions": transactions}
    )


@app.get("/add-transaction", response_class=HTMLResponse)
def show_add_transaction(request: Request):
    """
    Displays the HTML form for data entry.
    
    This is a simple GET request that just grabs the 'add_transaction.html' 
    child template and injects it into the base shell.
    """
    return templates.TemplateResponse("add_transaction.html", {"request": request})


@app.post("/add-transaction", response_class=RedirectResponse)
def process_add_transaction(
    txn_date: date = Form(...),
    txn_type: str = Form(...),
    category: str = Form(...),
    item_description: str = Form(...),
    qty: float = Form(...),
    unit_price: float = Form(...),
    payment_status: str = Form(...),
    remarks: str = Form(None),
    session: Session = Depends(get_session)
):
    """
    Intercepts the HTML form submission, saves the data, and redirects the user.
    
    Why we use Form(...):
    Unlike JSON APIs, HTML forms send data as 'x-www-form-urlencoded'. 
    The Form() tool tells FastAPI to look for those specific 'name' attributes 
    from the HTML inputs.
    """
    # 1. Calculate the Data Science Math (Total Amount) automatically!
    total_amount = qty * unit_price

    # 2. Build the exact blueprint expected by Postgres
    new_transaction = Transaction(
        txn_date=txn_date,
        txn_type=txn_type,
        category=category,
        item_description=item_description,
        qty=qty,
        unit_price=unit_price,
        total_amount=total_amount,
        payment_status=payment_status,
        remarks=remarks
    )

    # 3. Save it to the database
    session.add(new_transaction)
    session.commit()

    # 4. The 303 Redirect (Crucial UI/UX Step)
    # Instead of showing a blank "Success" screen, a 303 redirect forces the 
    # user's browser to immediately bounce back to the Home Page ('/') so 
    # they can visually verify their new data appeared in the ledger.
    return RedirectResponse(url="/", status_code=303)


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

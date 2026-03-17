from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import date
from typing import Optional


from src.database import engine
from src.models import (
    Transaction,
    CategoryEnum,
    StatusEnum,
    UnitOfMeasureEnum,
    TransactionTypeEnum,
)


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
    statement = select(Transaction).order_by(Transaction.txn_date.desc()).limit(10)
    transactions = session.exec(statement).all()

    # 2. Hand the web request and the data over to the HTML template
    return templates.TemplateResponse(
        "index.html", {"request": request, "transactions": transactions}
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
    txn_type: TransactionTypeEnum = Form(...),
    category: CategoryEnum = Form(...),
    item_description: str = Form(...),
    qty: float = Form(...),
    unit_of_measure: UnitOfMeasureEnum = Form(...),
    unit_price: float = Form(...),
    amount_paid: float = Form(...),
    payment_status: StatusEnum = Form(...),
    entity_name: Optional[str] = Form(None),
    reference_tag: Optional[str] = Form(None),
    remarks: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """
    Intercepts the HTML form submission, validates the financial metrics securely
    on the backend, and commits the new transaction to the PostgreSQL ledger.
    """

    # Prevent negative inputs from corrupting the financial data
    # Hackers or accidental typos could bypass the HTML frontend restrictions,
    # so we enforce a hard security wall here on the server side.
    if qty < 0 or unit_price < 0 or amount_paid < 0:
        raise HTTPException(
            status_code=400, detail="Financial values cannot be negative."
        )

    # Calculate the total amount securely on the backend
    # We never trust the frontend to send the total amount. By calculating it
    # here in Python, we guarantee the math is absolutely flawless for Pandas.
    total_amount = qty * unit_price

    # Map the validated form data to our strict database blueprint
    new_transaction = Transaction(
        txn_date=txn_date,
        txn_type=txn_type,
        category=category,
        item_description=item_description,
        qty=qty,
        unit_of_measure=unit_of_measure,
        unit_price=unit_price,
        total_amount=total_amount,
        amount_paid=amount_paid,
        payment_status=payment_status,
        entity_name=entity_name,
        reference_tag=reference_tag,
        remarks=remarks,
    )

    # Lock the transaction into the database vault
    session.add(new_transaction)
    session.commit()

    # Issue a redirect response to improve user experience
    # Instead of showing a blank success screen, this bounces the user
    # directly back to the main dashboard so they can visually verify their entry.
    return RedirectResponse(url="/", status_code=303)


@app.get("/ledger", response_class=HTMLResponse)
def read_ledger(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    payment_status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Master Ledger Search Engine.

    Only queries the database if at least one search parameter is provided.
    Otherwise, returns an empty list to keep the initial page load clean.
    """

    # Check if the user actually clicked 'Filter' with data
    user_provided_filters = any([start_date, end_date, category, payment_status])

    if not user_provided_filters:
        # If no filters, don't even bother asking Postgres. Just return empty.
        transactions = []
        has_searched = False
    else:
        # If they did search, build the dynamic query
        has_searched = True

        # The base query (grab everything, newest first)
        statement = select(Transaction).order_by(Transaction.txn_date.desc())

        # 2. Dynamically stack the filters (The "Mix and Match" Logic)
        if start_date:
            statement = statement.where(Transaction.txn_date >= start_date)

        if end_date:
            statement = statement.where(Transaction.txn_date <= end_date)

        if category:
            statement = statement.where(Transaction.category == category)

        if payment_status:
            statement = statement.where(Transaction.payment_status == payment_status)

        # 3. Execute the final, customized query
        transactions = session.exec(statement).all()

        # 4. Hand the exact filtered results to the ledger.html page
    return templates.TemplateResponse(
        "ledger.html",
        {
            "request": request,
            "transactions": transactions,
            "has_searched": has_searched,
        },
    )


@app.get("/edit-transaction/{id}", response_class=HTMLResponse)
def show_edit_transaction(
    id: int, request: Request, session: Session = Depends(get_session)
):
    """
    Step 1 of Editing: The GET Route

    Extracts the unique ID from the URL, finds that specific record in Postgres,
    and hands it to the edit form so Jinja2 can pre-fill the boxes.
    """
    # Grab the specific transaction
    transaction = session.get(Transaction, id)

    # Security check: What if they typed /edit-transaction/999 and it doesn't exist?
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return templates.TemplateResponse(
        "edit_transaction.html", {"request": request, "transaction": transaction}
    )


@app.post("/edit-transaction/{id}", response_class=RedirectResponse)
def process_edit_transaction(
    id: int,
    txn_date: date = Form(...),
    txn_type: str = Form(...),
    category: CategoryEnum = Form(...),
    item_description: str = Form(...),
    qty: float = Form(...),
    unit_price: float = Form(...),
    payment_status: StatusEnum = Form(...),
    remarks: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """
    Step 2 of Editing: The POST Route

    Catches the submitted form data, finds the original record,
    overwrites the old data with the newly typed data, and saves it.
    """
    # 1. Find the original record
    transaction = session.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # 2. Backend Security Check
    if qty < 0 or unit_price < 0:
        raise HTTPException(
            status_code=400, detail="Quantity and Price cannot be negative."
        )

    # 3. Overwrite the old values with the new form values
    transaction.txn_date = txn_date
    transaction.txn_type = txn_type
    transaction.category = category
    transaction.item_description = item_description
    transaction.qty = qty
    transaction.unit_price = unit_price
    transaction.total_amount = qty * unit_price  # Recalculate the math!
    transaction.payment_status = payment_status
    transaction.remarks = remarks

    # 4. Save and redirect back to the Ledger page
    session.add(transaction)
    session.commit()

    return RedirectResponse(url="/ledger", status_code=303)


@app.get("/transaction/{id}", response_class=HTMLResponse)
def view_transaction(
    id: int, request: Request, session: Session = Depends(get_session)
):
    """
    The View Route (Read)
    Fetches a single transaction and displays it on a dedicated receipt page.
    """
    transaction = session.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return templates.TemplateResponse(
        "view_transaction.html", {"request": request, "transaction": transaction}
    )


@app.post("/delete-transaction/{id}", response_class=RedirectResponse)
def delete_transaction(id: int, session: Session = Depends(get_session)):
    """
    The Delete Route (Destroy)
    Permanently removes a transaction from Postgres and reloads the ledger.
    """
    transaction = session.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(transaction)
    session.commit()

    # 303 Redirect forces the browser back to the Ledger
    return RedirectResponse(url="/ledger", status_code=303)


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

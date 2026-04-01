from fastapi import FastAPI, Request, Depends, Form, HTTPException, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import date, datetime
from typing import Optional


from src.database import engine
from src.security import hash_password, verify_password
from src.models import (
    Transaction,
    CategoryEnum,
    StatusEnum,
    UnitOfMeasureEnum,
    TransactionTypeEnum,
    User,
    UserRole,
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


def get_current_user(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: Session = Depends(get_session),
):
    """Check for a valid cookie before letting anyone pass"""

    if not farm_session:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"location": "/login"}
        )

    statement = select(User).where(User.username == farm_session)
    user = session.exec(statement).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"location": "/login"}
        )

    return user


@app.get("/register")
def show_register_page(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: Session = Depends(get_session),
):
    """Sends the register.html form page, but redirects if already logged in."""

    # --- THE REVERSE BOUNCER ---
    if farm_session:
        statement = select(User).where(User.username == farm_session)
        user = session.exec(statement).first()

        # If the badge is real and the user is active, kick them out of the register page!
        if user and user.is_active:
            return RedirectResponse(url="/dashboard", status_code=303)

    # If they don't have a badge (or it's fake), show them the blank form.
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def process_registration(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """Catches the form data, checks for duplicates and saves the user."""

    statement = select(User).where((User.username == username) | (User.email == email))
    existing_user = session.exec(statement).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Sorry, that username or email already exist!",
            },
        )
    encrypt_passw = hash_password(password)
    new_user = User(
        full_name=full_name,
        email=email,
        username=username,
        hashed_password=encrypt_passw,
        role=UserRole.STAFF,
        is_active=True,
    )
    session.add(new_user)
    session.commit()

    return RedirectResponse(url="/login? msg=registered", status_code=303)


@app.get("/login")
def login_route(
    request: Request,
    farm_session: str | None = Cookie(None),  # 1. Look for the badge
    session: Session = Depends(get_session),  # 2. Open the vault
):
    """Route users to the login html page, but redirects if already logged in."""

    # --- THE REVERSE BOUNCER ---
    if farm_session:
        statement = select(User).where(User.username == farm_session)
        user = session.exec(statement).first()

        # If the badge is real and the user is active, kick them out of the login page!
        if user and user.is_active:
            return RedirectResponse(url="/dashboard", status_code=303)

    # If they don't have a badge, show them the login form.
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def process_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """Verfies the password and hands out the VIP Cookie."""

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    user_pass = verify_password(password, user.hashed_password)
    if not user or not user_pass:
        return templates.TemplateResponse(
            "/login.html",
            {
                "request": request,
                "error": "Invalid Username or Password. Please Try Again.",
            },
        )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="farm_session", value=user.username, httponly=True, max_age=1200
    )
    return response


@app.get("/logout")
def logout_user():
    """Destroys the user's cookie and kicks them back to the login page."""

    # 1. Point them back to the login door, with a nice message
    response = RedirectResponse(url="/login?msg=logged_out", status_code=303)

    # 2. The Kill Switch: Tell the browser to delete the cookie!
    response.delete_cookie(key="farm_session")

    # 3. Hand the package back to the browser
    return response


@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: Session = Depends(get_session),
):
    """
    The Public StoreFront. AnyOne can see this
    """

    current_user = None
    if farm_session:
        statement = select(User).where(User.username == farm_session)
        current_user = session.exec(statement).first()

    # 2. Hand the web request and the data over to the HTML template
    return templates.TemplateResponse(
        "homepage.html",
        {
            "request": request,
            "user": current_user,
        },
    )


@app.get("/dashboard")
def read_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),  # The STRICT Tollbooth Guard
    session: Session = Depends(get_session),
):
    """The Secure Ledger. Must have a valid VIP Cookie."""

    # Grab the latest 10 transactions
    statement = select(Transaction).order_by(Transaction.txn_date.desc()).limit(10)
    transactions = session.exec(statement).all()

    return templates.TemplateResponse(
        "index.html",  # This still points to your ledger template!
        {"request": request, "user": current_user, "transactions": transactions},
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
    # 4. The 303 Redirect (Now with a success message flag!)
    return RedirectResponse(url="/?msg=saved", status_code=303)


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
    query = select(Transaction)

    if start_date and start_date.strip() != "":
        # Convert the string to a real PostgreSQL-friendly Date object
        parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.where(Transaction.txn_date >= parsed_start)

    # 3. Safely handle the end_date
    if end_date and end_date.strip() != "":
        parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.where(Transaction.txn_date <= parsed_end)

    # 4. Safely handle Category and Status (ignoring empty strings)
    if category and category.strip() != "":
        query = query.where(Transaction.category == category)

    if payment_status and payment_status.strip() != "":
        query = query.where(Transaction.payment_status == payment_status)

    # 5. Execute the final query
    transactions = session.exec(query.order_by(Transaction.txn_date.desc())).all()
    print(f"======== DEBUG: Python found {len(transactions)} rows! ========")

    return templates.TemplateResponse(
        "ledger.html", {"request": request, "transactions": transactions}
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
    Step 2 of Editing: The POST Route

    Catches the submitted form data, finds the original record,
    overwrites the old data with the newly typed V2 architecture data, and saves it.
    """
    # 1. Find the original record
    transaction = session.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # 2. Backend Security Check
    if qty < 0 or unit_price < 0 or amount_paid < 0:
        raise HTTPException(
            status_code=400, detail="Financial values cannot be negative."
        )

    # 3. Overwrite the old values with the new form values
    transaction.txn_date = txn_date
    transaction.txn_type = txn_type
    transaction.category = category
    transaction.item_description = item_description
    transaction.qty = qty
    transaction.unit_of_measure = unit_of_measure
    transaction.unit_price = unit_price
    transaction.total_amount = qty * unit_price  # Recalculate securely!
    transaction.amount_paid = amount_paid
    transaction.payment_status = payment_status
    transaction.entity_name = entity_name
    transaction.reference_tag = reference_tag
    transaction.remarks = remarks

    # 4. Save and redirect back to the Ledger page with an edit flag
    session.add(transaction)
    session.commit()
    return RedirectResponse(url="/ledger?msg=edited", status_code=303)


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
    # Redirect back to the Ledger with a delete flag
    return RedirectResponse(url="/ledger?msg=deleted", status_code=303)


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

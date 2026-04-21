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


app = FastAPI(
    title="Pig Farm ERP",
    description="In Progress",
    version="0.1.0",
)

templates = Jinja2Templates(directory="templates")


class AdminAccessDeniedException(Exception):
    """Triggered when a STAFF member tries to perform an ADMIN action."""

    pass


def get_session():
    """Dependency generator to manage database sessions.
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


def get_admin_user(current_user: User = Depends(get_current_user)):
    """The VIP Manager: Only allows users with the ADMIN role to pass."""

    if current_user.role != UserRole.ADMIN:
        raise AdminAccessDeniedException()

    return current_user


@app.exception_handler(AdminAccessDeniedException)
async def admin_access_denied_handler(
    request: Request, exc: AdminAccessDeniedException
):
    """
    The Catcher: If anyone pulls the AdminAccessDeniedException alarm anywhere
    in the app, this net catches them and bounces them to the ledger safely.
    """
    return RedirectResponse(url="/ledger?msg=denied", status_code=303)


def redirect_if_authenticated(
    farm_session: str | None = Cookie(None), session: Session = Depends(get_session)
):
    """The Anti-Bouncer: If you already have a VIP badge, you cannot enter here."""

    if farm_session:
        statement = select(User).where(User.username == farm_session)
        user = session.exec(statement).first()

        if user and user.is_active:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/dashboard"},
            )


@app.get("/register")
def show_register_page(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: Session = Depends(get_session),
    _guard: None = Depends(redirect_if_authenticated),
):
    """Sends the register.html form page, but redirects if already logged in."""

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

    return RedirectResponse(url="/login?msg=registered", status_code=303)


@app.get("/login")
def login_route(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: Session = Depends(get_session),
    _guard: None = Depends(redirect_if_authenticated),
):
    """Route users to the login html page, but redirects if already logged in."""

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

    response = RedirectResponse(url="/login?msg=logged_out", status_code=303)
    response.delete_cookie(key="farm_session")
    return response


@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: Session = Depends(get_session),
):
    """The Public StoreFront. AnyOne can see this"""

    current_user = None
    if farm_session:
        statement = select(User).where(User.username == farm_session)
        current_user = session.exec(statement).first()

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
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """The Secure Ledger. Must have a valid VIP Cookie."""

    statement = select(Transaction).order_by(Transaction.txn_date.desc()).limit(10)
    transactions = session.exec(statement).all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": current_user, "transactions": transactions},
    )


@app.get("/add-transaction", response_class=HTMLResponse)
def show_add_transaction(
    request: Request, current_user: User = Depends(get_current_user)
):
    """Displays the HTML form for data entry."""

    return templates.TemplateResponse(
        "add_transaction.html",
        {
            "request": request,
            "user": current_user,
        },
    )


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
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Intercepts the HTML form submission, validates the financial metrics securely
    on the backend, and commits the new transaction to the PostgreSQL ledger.
    """

    if qty < 0 or unit_price < 0 or amount_paid < 0:
        raise HTTPException(
            status_code=400, detail="Financial values cannot be negative."
        )

    total_amount = qty * unit_price
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
        user_id=current_user.id,
    )

    session.add(new_transaction)
    session.commit()

    return RedirectResponse(url="/?msg=saved", status_code=303)


@app.get("/ledger", response_class=HTMLResponse)
def read_ledger(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    payment_status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Master Ledger Search Engine. Only queries the database if at least one search parameter is provided.
    Otherwise, returns an empty list to keep the initial page load clean.
    """

    query = select(Transaction)

    if start_date and start_date.strip() != "":
        parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.where(Transaction.txn_date >= parsed_start)

    if end_date and end_date.strip() != "":
        parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.where(Transaction.txn_date <= parsed_end)

    if category and category.strip() != "":
        query = query.where(Transaction.category == category)

    if payment_status and payment_status.strip() != "":
        query = query.where(Transaction.payment_status == payment_status)

    transactions = session.exec(query.order_by(Transaction.txn_date.desc())).all()

    return templates.TemplateResponse(
        "ledger.html",
        {"request": request, "user": current_user, "transactions": transactions},
    )


@app.get("/edit-transaction/{id}", response_class=HTMLResponse)
def show_edit_transaction(
    id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Extracts the unique ID from the URL, finds that specific record in Postgres,
    and hands it to the edit form so Jinja2 can pre-fill the boxes.
    """

    transaction = session.get(Transaction, id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return templates.TemplateResponse(
        "edit_transaction.html",
        {"request": request, "user": current_user, "transaction": transaction},
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
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Catches the submitted form data, finds the original record, overwrites the old data with the newly typed data, and saves it."""

    transaction = session.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if qty < 0 or unit_price < 0 or amount_paid < 0:
        raise HTTPException(
            status_code=400, detail="Financial values cannot be negative."
        )

    transaction.txn_date = txn_date
    transaction.txn_type = txn_type
    transaction.category = category
    transaction.item_description = item_description
    transaction.qty = qty
    transaction.unit_of_measure = unit_of_measure
    transaction.unit_price = unit_price
    transaction.total_amount = qty * unit_price
    transaction.amount_paid = amount_paid
    transaction.payment_status = payment_status
    transaction.entity_name = entity_name
    transaction.reference_tag = reference_tag
    transaction.remarks = remarks

    session.add(transaction)
    session.commit()
    return RedirectResponse(url="/ledger?msg=edited", status_code=303)


@app.get("/transaction/{id}", response_class=HTMLResponse)
def view_transaction(
    id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """The View Route (Read)Fetches a single transaction and displays it on a dedicated receipt page."""

    transaction = session.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return templates.TemplateResponse(
        "view_transaction.html",
        {"request": request, "user": current_user, "transaction": transaction},
    )


@app.post("/delete-transaction/{id}", response_class=RedirectResponse)
def delete_transaction(
    id: int,
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """The Delete Route (Destroy)Permanently removes a transaction from Postgres and reloads the ledger."""

    transaction = session.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(transaction)
    session.commit()

    return RedirectResponse(url="/ledger?msg=deleted", status_code=303)


@app.get("/settings", response_class=HTMLResponse)
def show_settings_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Sees the user profile and settings dashboard."""

    return templates.TemplateResponse(
        "profile.html", {"request": request, "user": current_user}
    )


@app.post("/settings/update-info", response_class=RedirectResponse)
def update_personal_info(
    full_name: str = Form(...),
    email: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Catches the profile update form and saves the new name and email to the database."""

    current_user.full_name = full_name
    current_user.email = email

    session.add(current_user)
    session.commit()

    return RedirectResponse(url="/settings?msg=updated", status_code=303)


@app.post("/settings/update-password", response_class=RedirectResponse)
def update_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Highly secure route to update a user's password. Requires verification of the user's password to prevent unauthorized changes."""

    if new_password != confirm_password:
        return RedirectResponse(url="/settings?msg=password_mismatch", status_code=303)

    if not verify_password(current_password, current_user.hashed_password):
        return RedirectResponse(url="/settings?msg=wrong_password", status_code=303)

    current_user.hashed_password = hash_password(new_password)

    session.add(current_user)
    session.commit()

    return RedirectResponse(url="/settings?msg=password_updated", status_code=303)


@app.post("/transactions/", response_model=Transaction)
def create_transaction(
    transaction: Transaction,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
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
def read_transactions(
    current_user: User = Depends(get_current_user),
):

    with Session(engine) as session:
        statement = select(Transaction)
        results = session.exec(statement).all()
        return results

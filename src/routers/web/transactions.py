from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.dependencies import get_admin_user, get_current_user
from src.models import (
    CategoryEnum,
    StatusEnum,
    Transaction,
    TransactionTypeEnum,
    UnitOfMeasureEnum,
    User,
)
from src.schemas.transaction import TransactionCreate
from src.services.transaction import (
    create_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)
from src.templating import templates

router = APIRouter()


@router.get("/dashboard")
async def read_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """The Secure Ledger. Must have a valid VIP Cookie."""

    statement = (
        select(Transaction)
        .options(selectinload(Transaction.user))
        .order_by(Transaction.txn_date.desc())
        .limit(10)
    )
    results = await session.exec(statement)
    transactions = results.all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": current_user, "transactions": transactions},
    )


@router.get("/add-transaction", response_class=HTMLResponse)
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


@router.post("/add-transaction", response_class=RedirectResponse)
async def process_add_transaction(
    txn_date: date = Form(...),
    txn_type: TransactionTypeEnum = Form(...),
    category: CategoryEnum = Form(...),
    item_description: str = Form(...),
    qty: float = Form(...),
    unit_of_measure: UnitOfMeasureEnum = Form(...),
    unit_price: float = Form(...),
    amount_paid: float = Form(...),
    entity_name: str | None = Form(None),
    reference_tag: str | None = Form(None),
    remarks: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Intercepts the HTML form submission, converts the form into a
    transaction and redirects new transaction to the PostgreSQL ledger.
    """

    data = TransactionCreate(
        txn_date=txn_date,
        txn_type=txn_type,
        category=category,
        item_description=item_description,
        qty=qty,
        unit_of_measure=unit_of_measure,
        unit_price=unit_price,
        amount_paid=amount_paid,
        entity_name=entity_name,
        reference_tag=reference_tag,
        remarks=remarks,
    )

    try:
        await create_transaction(session=session, data=data, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return RedirectResponse(url="/?msg=saved", status_code=303)


@router.get("/ledger", response_class=HTMLResponse)
async def read_ledger(
    request: Request,
    start_date: str | None = None,
    end_date: str | None = None,
    category: str | None = None,
    payment_status: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Master Ledger Search Engine.
    Only queries the database if at least one search parameter is provided.
    Otherwise, returns an empty list to keep the initial page load clean.
    """
    parsed_start = None
    parsed_end = None
    parsed_category = None
    parsed_payment_status = None

    if start_date and start_date.strip() != "":
        parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date and end_date.strip() != "":
        parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
    if category and category.strip() != "":
        parsed_category = CategoryEnum[category]
    if payment_status and payment_status.strip() != "":
        parsed_payment_status = StatusEnum[payment_status]

    transactions = await list_transactions(
        session=session,
        category=parsed_category,
        start_date=parsed_start,
        end_date=parsed_end,
        payment_status=parsed_payment_status,
    )

    return templates.TemplateResponse(
        "ledger.html",
        {"request": request, "user": current_user, "transactions": transactions},
    )


@router.get("/transaction/{id}", response_class=HTMLResponse)
async def view_transaction(
    id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """The View Route (Read)Fetches a single transaction,
    and displays it on a dedicated receipt page."""

    transaction = await get_transaction(session, id)

    return templates.TemplateResponse(
        "view_transaction.html",
        {"request": request, "user": current_user, "transaction": transaction},
    )


@router.get("/edit-transaction/{id}", response_class=HTMLResponse)
async def show_edit_transaction(
    id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Extracts the unique ID from the URL, finds that specific record in Postgres,
    and hands it to the edit form so Jinja2 can pre-fill the boxes.
    """

    transaction = await get_transaction(session, id)

    return templates.TemplateResponse(
        "edit_transaction.html",
        {"request": request, "user": current_user, "transaction": transaction},
    )


@router.post("/edit-transaction/{id}", response_class=RedirectResponse)
async def process_edit_transaction(
    id: int,
    txn_date: date = Form(...),
    txn_type: TransactionTypeEnum = Form(...),
    category: CategoryEnum = Form(...),
    item_description: str = Form(...),
    qty: float = Form(...),
    unit_of_measure: UnitOfMeasureEnum = Form(...),
    unit_price: float = Form(...),
    amount_paid: float = Form(...),
    entity_name: str | None = Form(None),
    reference_tag: str | None = Form(None),
    remarks: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Catches the submitted form data, finds the original record,
    overwrites the old data with the newly typed data, and saves it."""

    data = TransactionCreate(
        txn_date=txn_date,
        txn_type=txn_type,
        category=category,
        item_description=item_description,
        qty=qty,
        unit_of_measure=unit_of_measure,
        unit_price=unit_price,
        amount_paid=amount_paid,
        entity_name=entity_name,
        reference_tag=reference_tag,
        remarks=remarks,
    )

    try:
        await update_transaction(session, id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return RedirectResponse(url="/ledger?msg=edited", status_code=303)


@router.post("/delete-transaction/{id}", response_class=RedirectResponse)
async def delete_transaction_endpoint(
    id: int,
    admin_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    """The Delete Route (Destroy)Permanently
    removes a transaction from Postgres and reloads the ledger."""

    await delete_transaction(session, id)

    return RedirectResponse(url="/ledger?msg=deleted", status_code=303)

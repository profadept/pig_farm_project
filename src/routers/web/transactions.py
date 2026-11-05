from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.dependencies import get_current_user
from src.models import (
    Transaction,
    User,
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

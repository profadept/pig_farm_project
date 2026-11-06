from fastapi import Cookie, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.exceptions import AdminAccessDeniedException, TransactionNotFoundError
from src.models import (
    User,
)
from src.routers.api import transactions as api_transactions
from src.routers.web import auth as web_auth
from src.routers.web import transactions as web_transactions
from src.templating import templates

app = FastAPI(
    title="Pig Farm ERP",
    description="In Progress",
    version="0.1.0",
)
app.include_router(web_transactions.router)
app.include_router(api_transactions.router)
app.include_router(web_auth.router)


@app.exception_handler(AdminAccessDeniedException)
async def admin_access_denied_handler(
    request: Request, exc: AdminAccessDeniedException
):
    """
    The Catcher: If anyone pulls the AdminAccessDeniedException alarm anywhere
    in the app, this net catches them and bounces them to the ledger safely.
    """
    return RedirectResponse(url="/ledger?msg=denied", status_code=303)


@app.exception_handler(TransactionNotFoundError)
async def transaction_not_found_handler(
    request: Request, exc: TransactionNotFoundError
):
    return RedirectResponse(url="/ledger?msg=not_found", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: AsyncSession = Depends(get_session),
):
    """The Public StoreFront. AnyOne can see this"""

    current_user = None
    if farm_session:
        statement = select(User).where(User.username == farm_session)
        result = await session.exec(statement)
        current_user = result.first()

    return templates.TemplateResponse(
        "homepage.html",
        {
            "request": request,
            "user": current_user,
        },
    )

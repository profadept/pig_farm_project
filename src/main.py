from fastapi import Cookie, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.exception_handlers import (
    admin_access_denied_handler,
    transaction_not_found_handler,
)
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
app.add_exception_handler(AdminAccessDeniedException, admin_access_denied_handler)
app.add_exception_handler(TransactionNotFoundError, transaction_not_found_handler)


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

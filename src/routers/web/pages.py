from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.models import (
    User,
)
from src.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
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

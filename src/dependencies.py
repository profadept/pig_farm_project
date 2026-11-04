from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.exceptions import AdminAccessDeniedException
from src.models import User, UserRole


async def get_current_user(
    request: Request,
    farm_session: str | None = Cookie(None),
    session: AsyncSession = Depends(get_session),
):
    """Check for a valid cookie before letting anyone pass"""

    if not farm_session:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"location": "/login"}
        )

    statement = select(User).where(User.username == farm_session)
    result = await session.exec(statement)
    user = result.first()

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


async def redirect_if_authenticated(
    farm_session: str | None = Cookie(None),
    session: AsyncSession = Depends(get_session),
):
    """The Anti-Bouncer: If you already have a VIP badge, you cannot enter here."""

    if farm_session:
        statement = select(User).where(User.username == farm_session)
        result = await session.exec(statement)
        user = result.first()

        if user and user.is_active:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/dashboard"},
            )

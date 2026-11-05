from fastapi import Cookie, Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.dependencies import get_current_user, redirect_if_authenticated
from src.exceptions import AdminAccessDeniedException, TransactionNotFoundError
from src.models import (
    User,
    UserRole,
)
from src.routers.api import transactions as api_transactions
from src.routers.web import transactions as web_transactions
from src.security import hash_password, verify_password
from src.templating import templates

app = FastAPI(
    title="Pig Farm ERP",
    description="In Progress",
    version="0.1.0",
)
app.include_router(web_transactions.router)
app.include_router(api_transactions.router)


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


@app.get("/register")
async def show_register_page(
    request: Request,
    _guard: None = Depends(redirect_if_authenticated),
):
    """Sends the register.html form page, but redirects if already logged in."""

    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def process_registration(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    """Catches the form data, checks for duplicates and saves the user."""

    statement = select(User).where((User.username == username) | (User.email == email))
    result = await session.exec(statement)
    existing_user = result.first()

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
    await session.commit()

    return RedirectResponse(url="/login?msg=registered", status_code=303)


@app.get("/login")
async def login_route(
    request: Request,
    _guard: None = Depends(redirect_if_authenticated),
):
    """Route users to the login html page, but redirects if already logged in."""

    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def process_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    """Verfies the password and hands out the VIP Cookie."""

    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    user = result.first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
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


@app.get("/settings", response_class=HTMLResponse)
def show_settings_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Sees the user profile and settings dashboard."""

    return templates.TemplateResponse(
        "profile.html", {"request": request, "user": current_user}
    )


@app.post("/settings/update-info", response_class=RedirectResponse)
async def update_personal_info(
    full_name: str = Form(...),
    email: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Catches the profile update form and saves the new name and email to the database.
    """

    current_user.full_name = full_name
    current_user.email = email

    session.add(current_user)
    await session.commit()

    return RedirectResponse(url="/settings?msg=updated", status_code=303)


@app.post("/settings/update-password", response_class=RedirectResponse)
async def update_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Highly secure route to update a user's password.
    Requires verification of the user's password to prevent unauthorized changes."""

    if new_password != confirm_password:
        return RedirectResponse(url="/settings?msg=password_mismatch", status_code=303)

    if not verify_password(current_password, current_user.hashed_password):
        return RedirectResponse(url="/settings?msg=wrong_password", status_code=303)

    current_user.hashed_password = hash_password(new_password)

    session.add(current_user)
    await session.commit()

    return RedirectResponse(url="/settings?msg=password_updated", status_code=303)

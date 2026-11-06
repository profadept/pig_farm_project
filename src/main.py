from fastapi import FastAPI

from src.exception_handlers import (
    admin_access_denied_handler,
    transaction_not_found_handler,
)
from src.exceptions import AdminAccessDeniedException, TransactionNotFoundError
from src.routers.api import transactions as api_transactions
from src.routers.web import auth as web_auth
from src.routers.web import pages as web_pages
from src.routers.web import transactions as web_transactions

app = FastAPI(
    title="Pig Farm ERP",
    description="In Progress",
    version="0.1.0",
)
app.include_router(web_transactions.router)
app.include_router(api_transactions.router)
app.include_router(web_auth.router)
app.include_router(web_pages.router)
app.add_exception_handler(AdminAccessDeniedException, admin_access_denied_handler)
app.add_exception_handler(TransactionNotFoundError, transaction_not_found_handler)

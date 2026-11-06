from fastapi import Request
from fastapi.responses import RedirectResponse

from src.exceptions import AdminAccessDeniedException, TransactionNotFoundError


async def admin_access_denied_handler(
    request: Request, exc: AdminAccessDeniedException
):
    """
    The Catcher: If anyone pulls the AdminAccessDeniedException alarm anywhere
    in the app, this net catches them and bounces them to the ledger safely.
    """
    return RedirectResponse(url="/ledger?msg=denied", status_code=303)


async def transaction_not_found_handler(
    request: Request, exc: TransactionNotFoundError
):
    return RedirectResponse(url="/ledger?msg=not_found", status_code=303)

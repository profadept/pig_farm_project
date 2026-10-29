class TransactionNotFoundError(Exception):
    """Raised when a Transaction is not found"""


class AdminAccessDeniedException(Exception):
    """Triggered when a STAFF member tries to perform an ADMIN action."""

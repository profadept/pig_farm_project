from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.transaction import StatusEnum, Transaction
from src.schemas.transaction import TransactionCreate


def compute_transaction_totals(qty, unit_price, amount_paid):

    if qty < 0 or unit_price < 0 or amount_paid < 0:
        raise ValueError("Financial value cannot be negative")

    total_amount = qty * unit_price

    if total_amount == 0:
        raise ValueError("Total amount must be greater than zero")
    if amount_paid > total_amount:
        raise ValueError("Amount paid cannot exceed total amount")

    if amount_paid == 0:
        payment_status = StatusEnum.unpaid
    elif amount_paid < total_amount:
        payment_status = StatusEnum.partially_paid
    else:
        payment_status = StatusEnum.paid

    return total_amount, payment_status


async def create_transaction(
    session: AsyncSession, data: TransactionCreate, user_id: int
) -> Transaction:
    total_amount, payment_status = compute_transaction_totals(
        qty=data.qty, unit_price=data.unit_price, amount_paid=data.amount_paid
    )

    transaction = Transaction(
        **data.model_dump(),
        total_amount=total_amount,
        payment_status=payment_status,
        user_id=user_id,
    )

    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction

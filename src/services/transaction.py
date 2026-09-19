from src.models.transaction import StatusEnum


def compute_transaction_totals(qty, unit_price, amount_paid):

    if qty < 0 or unit_price < 0 or amount_paid < 0:
        raise ValueError("Financial value cannot be negative")

    total_amount = qty * unit_price

    if amount_paid == 0 and total_amount > 0:
        payment_status = StatusEnum.unpaid
    elif amount_paid > 0 and amount_paid < total_amount:
        payment_status = StatusEnum.partially_paid
    elif amount_paid >= total_amount and total_amount > 0:
        payment_status = StatusEnum.paid
    else:
        payment_status = StatusEnum.unpaid

    return total_amount, payment_status

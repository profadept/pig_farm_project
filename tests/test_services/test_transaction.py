import pytest

from src.models.transaction import StatusEnum
from src.schemas.transaction import TransactionCreate
from src.services.transaction import compute_transaction_totals, create_transaction


def test_compute_totals_paid():
    total, status = compute_transaction_totals(qty=5, unit_price=100, amount_paid=500)
    assert total == 500
    assert status == StatusEnum.paid


def test_compute_totals_partially_paid():
    total, status = compute_transaction_totals(qty=5, unit_price=100, amount_paid=200)
    assert total == 500
    assert status == StatusEnum.partially_paid


def test_compute_totals_unpaid():
    total, status = compute_transaction_totals(qty=10, unit_price=100, amount_paid=0)
    assert total == 1000
    assert status == StatusEnum.unpaid


def test_compute_totals_negative_raises():
    with pytest.raises(ValueError):
        compute_transaction_totals(qty=-1, unit_price=100, amount_paid=0)


def test_compute_totals_zero_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        compute_transaction_totals(qty=10, unit_price=0, amount_paid=100)


def test_compute_totals_overpaid_raises():
    with pytest.raises(ValueError, match="cannot exceed"):
        compute_transaction_totals(qty=5, unit_price=100, amount_paid=600)


async def test_create_transaction_saves_with_computed_total(test_session, test_user):
    data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Transport & Logistics",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=1500,
        entity_name="Public Transport",
        reference_tag="Test",
    )

    transaction = await create_transaction(test_session, data, test_user.id)

    assert transaction.total_amount == 2000
    assert transaction.payment_status == StatusEnum.partially_paid
    assert transaction.user_id == test_user.id


async def test_create_transaction_reject_overpaid_amount(test_session, test_user):
    data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Transport & Logistics",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=2500,
        entity_name="Public Transport",
        reference_tag="Test",
    )

    with pytest.raises(ValueError, match="cannot exceed"):
        await create_transaction(test_session, data, test_user.id)

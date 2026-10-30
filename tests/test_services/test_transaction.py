import pytest

from src.exceptions import TransactionNotFoundError
from src.models.transaction import StatusEnum
from src.schemas.transaction import TransactionCreate
from src.services.transaction import (
    compute_transaction_totals,
    create_transaction,
    get_transaction,
    update_transaction,
)


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


async def test_get_transaction_returns_saved_transaction(test_session, test_user):
    data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Transport & Logistics",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=2000,
        entity_name="Public Transport",
        reference_tag="Test",
    )

    saved = await create_transaction(test_session, data, test_user.id)

    found = await get_transaction(test_session, saved.id)

    assert found.id == saved.id


async def test_get_transaction_not_found_raises(test_session):
    with pytest.raises(TransactionNotFoundError):
        await get_transaction(test_session, 9999999)


async def test_update_transaction_compute_totals(test_session, test_user):
    save_data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Transport & Logistics",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=0,
        entity_name="Public Transport",
        reference_tag="Test",
    )

    saved = await create_transaction(test_session, save_data, test_user.id)

    update_data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Transport & Logistics",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=2000,
        entity_name="Public Transport",
        reference_tag="Test",
    )

    updated = await update_transaction(test_session, saved.id, update_data)

    assert updated.total_amount == 2000
    assert updated.payment_status == StatusEnum.paid


async def test_update_transaction_overpaid_raises_and_keeps_row(
    test_session, test_user
):
    save_data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Transport & Logistics",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=0,
        entity_name="Public Transport",
        reference_tag="Test",
    )

    saved = await create_transaction(test_session, save_data, test_user.id)

    bad_data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Transport & Logistics",
        item_description="Changed",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=3000,
        entity_name="Public Transport",
        reference_tag="Test",
    )

    with pytest.raises(ValueError, match="cannot exceed"):
        await update_transaction(test_session, saved.id, bad_data)

    unchanged = await get_transaction(test_session, saved.id)

    assert unchanged.amount_paid == 0
    assert unchanged.item_description == "Commute to Farm"

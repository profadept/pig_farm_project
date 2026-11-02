from datetime import date

import pytest

from src.exceptions import TransactionNotFoundError
from src.models.transaction import CategoryEnum, StatusEnum
from src.schemas.transaction import TransactionCreate
from src.services.transaction import (
    compute_transaction_totals,
    create_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
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


async def test_delete_transaction_removes_row(test_session, test_user):
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

    await delete_transaction(test_session, saved.id)

    with pytest.raises(TransactionNotFoundError):
        await get_transaction(test_session, saved.id)


async def test_delete_transaction_not_found_raises(test_session):
    with pytest.raises(TransactionNotFoundError):
        await delete_transaction(test_session, 9999999)


async def test_list_transaction_filters_by_payment_status(test_session, test_user):
    unpaid_data = TransactionCreate(
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
    await create_transaction(test_session, unpaid_data, test_user.id)

    paid_data = TransactionCreate(
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
    paid = await create_transaction(test_session, paid_data, test_user.id)

    result = await list_transactions(test_session, payment_status=StatusEnum.paid)

    assert [t.id for t in result] == [paid.id]


async def test_list_transaction_filters_by_date_range(test_session, test_user):
    date_1_data = TransactionCreate(
        txn_date="2026-08-01",
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
    await create_transaction(test_session, date_1_data, test_user.id)

    date_2_data = TransactionCreate(
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
    middle = await create_transaction(test_session, date_2_data, test_user.id)

    date_3_data = TransactionCreate(
        txn_date="2026-08-30",
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
    await create_transaction(test_session, date_3_data, test_user.id)

    result = await list_transactions(
        test_session, start_date=date(2026, 8, 10), end_date=date(2026, 8, 20)
    )

    assert [t.id for t in result] == [middle.id]


async def test_list_transaction_filters_by_category(test_session, test_user):
    feed_data = TransactionCreate(
        txn_date="2026-08-16",
        txn_type="Expense",
        category="Feed",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=2000,
        entity_name="Public Transport",
        reference_tag="Test",
    )
    feed = await create_transaction(test_session, feed_data, test_user.id)

    transport_data = TransactionCreate(
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
    await create_transaction(test_session, transport_data, test_user.id)

    result = await list_transactions(test_session, category=CategoryEnum.feed)

    assert [t.id for t in result] == [feed.id]


async def test_list_transaction_orders_newest_first(test_session, test_user):
    older_data = TransactionCreate(
        txn_date="2026-08-01",
        txn_type="Expense",
        category="Feed",
        item_description="Commute to Farm",
        qty=1,
        unit_of_measure="Head",
        unit_price=2000,
        amount_paid=2000,
        entity_name="Public Transport",
        reference_tag="Test",
    )
    older = await create_transaction(test_session, older_data, test_user.id)

    newer_data = TransactionCreate(
        txn_date="2026-08-20",
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
    newer = await create_transaction(test_session, newer_data, test_user.id)

    result = await list_transactions(test_session)

    assert [t.id for t in result] == [newer.id, older.id]

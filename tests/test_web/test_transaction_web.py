import pytest

from src.exceptions import TransactionNotFoundError
from src.models.transaction import StatusEnum
from src.services.transaction import (
    TransactionCreate,
    create_transaction,
    get_transaction,
)


async def test_view_missing_transaction_redirects_to_ledger(test_login):
    response = await test_login.get("/transaction/999999")

    assert response.status_code == 303
    assert response.headers["location"] == "/ledger?msg=not_found"


async def test_view_existing_transaction_returns_page(
    test_login, test_session, test_user
):
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

    saved = await create_transaction(
        session=test_session, data=data, user_id=test_user.id
    )

    response = await test_login.get(f"/transaction/{saved.id}")

    assert response.status_code == 200


async def test_edit_missing_transaction_redirects_to_ledger(test_login):
    response = await test_login.get("/edit-transaction/999999")

    assert response.status_code == 303
    assert response.headers["location"] == "/ledger?msg=not_found"


async def test_edit_missing_transaction_post_redirects_to_ledger(test_login):

    data = {
        "txn_date": "2026-08-16",
        "txn_type": "Expense",
        "category": "Transport & Logistics",
        "item_description": "Commute to Farm",
        "qty": 1,
        "unit_of_measure": "Head",
        "unit_price": 2000,
        "amount_paid": 1500,
        "entity_name": "Public Transport",
        "reference_tag": "Test",
    }

    response = await test_login.post("/edit-transaction/999999", data=data)

    assert response.status_code == 303
    assert response.headers["location"] == "/ledger?msg=not_found"


async def test_delete_missing_transaction_redirects_to_ledger(test_login):
    response = await test_login.post("/delete-transaction/999999")

    assert response.status_code == 303
    assert response.headers["location"] == "/ledger?msg=not_found"


async def test_delete_existing_transaction_removes_it(
    test_login, test_session, test_user
):
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

    saved = await create_transaction(
        session=test_session, data=data, user_id=test_user.id
    )

    response = await test_login.post(f"/delete-transaction/{saved.id}")

    assert response.status_code == 303
    assert response.headers["location"] == "/ledger?msg=deleted"

    with pytest.raises(TransactionNotFoundError):
        await get_transaction(test_session, saved.id)


async def test_edit_existing_transaction_updates_it(
    test_login, test_session, test_user
):

    saved_data = TransactionCreate(
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

    saved = await create_transaction(test_session, saved_data, test_user.id)

    update_data = {
        "txn_date": "2026-08-16",
        "txn_type": "Expense",
        "category": "Transport & Logistics",
        "item_description": "Commute to Farm",
        "qty": 1,
        "unit_of_measure": "Head",
        "unit_price": 2000,
        "amount_paid": 2000,
        "entity_name": "Public Transport",
        "reference_tag": "Test",
    }

    response = await test_login.post(f"/edit-transaction/{saved.id}", data=update_data)

    assert response.status_code == 303
    assert response.headers["location"] == "/ledger?msg=edited"

    updated = await get_transaction(test_session, saved.id)

    assert updated.amount_paid == 2000
    assert updated.payment_status == StatusEnum.paid


async def test_edit_overpaid_transaction_returns_400(
    test_login, test_session, test_user
):
    saved_data = TransactionCreate(
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

    saved = await create_transaction(test_session, saved_data, test_user.id)

    bad_data = {
        "txn_date": "2026-08-16",
        "txn_type": "Expense",
        "category": "Transport & Logistics",
        "item_description": "Commute to Farm",
        "qty": 1,
        "unit_of_measure": "Head",
        "unit_price": 2000,
        "amount_paid": 3000,
        "entity_name": "Public Transport",
        "reference_tag": "Test",
    }

    response = await test_login.post(f"/edit-transaction/{saved.id}", data=bad_data)

    assert response.status_code == 400

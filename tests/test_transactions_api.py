from sqlmodel import select

from src.models.transaction import StatusEnum, Transaction


async def test_create_transaction_partially_paid(test_login):

    transaction_response = await test_login.post(
        "/transactions/",
        json={
            "txn_date": "2026-08-16",
            "txn_type": "Expense",
            "category": "Transport & Logistics",
            "item_description": "Commute to Farm",
            "qty": 1,
            "unit_of_measure": "Head",
            "unit_price": 2000,
            "amount_paid": 1500,
            "total_amount": 2000,
            "payment_status": "Partially Paid",
            "entity_name": "Public Transport",
            "reference_tag": "Test",
        },
    )

    assert transaction_response.status_code == 200

    assert transaction_response.json()["payment_status"] == "Partially Paid"


async def test_process_add_transaction_payment_status(test_login, test_session):

    transaction_add = await test_login.post(
        "/add-transaction",
        data={
            "txn_date": "2026-08-16",
            "txn_type": "Expense",
            "category": "Transport & Logistics",
            "item_description": "Commute to Farm",
            "qty": 1,
            "unit_of_measure": "Head",
            "unit_price": 2000,
            "amount_paid": 1500,
            "total_amount": 2000,
            "payment_status": "Paid",
            "entity_name": "Public Transport",
            "reference_tag": "Test",
        },
    )

    assert transaction_add.status_code == 303

    statement = select(Transaction).where(
        Transaction.item_description == "Commute to Farm"
    )
    result = await test_session.exec(statement)
    saved_transaction = result.first()

    assert saved_transaction is not None
    assert saved_transaction.payment_status == StatusEnum.partially_paid

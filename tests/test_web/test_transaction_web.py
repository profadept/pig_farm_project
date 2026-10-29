from src.services.transaction import TransactionCreate, create_transaction


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

import pytest

from src.models.transaction import StatusEnum
from src.services.transaction import compute_transaction_totals


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

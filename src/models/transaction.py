from datetime import date
from enum import StrEnum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class TransactionTypeEnum(StrEnum):
    income = "Income"
    expense = "Expense"


class CategoryEnum(StrEnum):
    """The upgraded VIP list for strict financial categorization."""

    livestock_sales = "Livestock Sales"
    byproduct_sales = "Crop/Byproduct Sales"
    other_income = "Other Income"

    feed = "Feed"
    medicine = "Medicine & Vaccines"
    labor = "Labor"
    assets = "Assets & Equipment"
    livestock_purchases = "Livestock Purchases"
    maintenance = "Maintenance"
    utilities = "Utilities"
    consumables = "Consumables"
    transport = "Transport & Logistics"
    other_expense = "Other Expense"


class UnitOfMeasureEnum(StrEnum):
    """Base metrics to ensure accurate Pandas calculations."""

    kg = "kg"
    liters = "Liters"
    head = "Head"
    month = "Month"
    day = "Day"
    job = "Job/Item"
    other = "Other"
    ml = "ml"
    grams = "grams"


class StatusEnum(StrEnum):
    paid = "Paid"
    unpaid = "Unpaid"
    partially_paid = "Partially Paid"


class Transaction(SQLModel, table=True):
    """
    The Master Accounting Ledger.
    Tracks all cash flow in and out of the farm with strict data typing.
    """

    __tablename__ = "farm_transactions"

    id: int | None = Field(default=None, primary_key=True)

    txn_date: date
    txn_type: TransactionTypeEnum
    category: CategoryEnum
    item_description: str

    qty: float
    unit_of_measure: UnitOfMeasureEnum
    unit_price: float
    total_amount: float
    amount_paid: float
    payment_status: StatusEnum

    entity_name: str | None = Field(default=None)
    reference_tag: str | None = Field(default=None)
    remarks: str | None = Field(default=None)

    user_id: int | None = Field(default=None, foreign_key="users.id")

    user: Optional["User"] = Relationship(back_populates="transactions")  # noqa: F821

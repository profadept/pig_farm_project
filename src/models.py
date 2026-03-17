from enum import Enum
from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

# ---------------------------------------------------------
# ENUMS: The Strict VIP Lists (Data Science Protection)
# ---------------------------------------------------------


class TransactionTypeEnum(str, Enum):
    income = "Income"
    expense = "Expense"


class CategoryEnum(str, Enum):
    """The upgraded VIP list for strict financial categorization."""

    # Income Categories
    livestock_sales = "Livestock Sales"
    byproduct_sales = "Crop/Byproduct Sales"
    other_income = "Other Income"

    # Expense Categories
    feed = "Feed"
    medicine = "Medicine & Vaccines"
    labor = "Labor"
    assets = "Assets & Equipment"
    maintenance = "Maintenance"
    utilities = "Utilities"
    consumables = "Consumables"
    transport = "Transport & Logistics"
    other_expense = "Other Expense"


class UnitOfMeasureEnum(str, Enum):
    """Base metrics to ensure accurate Pandas calculations."""

    kg = "kg"
    liters = "Liters"
    head = "Head"
    month = "Month"
    day = "Day"
    job = "Job/Item"
    other = "Other"


class StatusEnum(str, Enum):
    paid = "Paid"
    unpaid = "Unpaid"
    partially_paid = "Partially Paid"


# ---------------------------------------------------------
# DATABASE MODELS: The Postgres Blueprints
# ---------------------------------------------------------


class Transaction(SQLModel, table=True):
    """
    The Master Accounting Ledger.
    Tracks all cash flow in and out of the farm with strict data typing.
    """

    __tablename__ = "farm_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Core Details
    txn_date: date
    txn_type: TransactionTypeEnum
    category: CategoryEnum
    item_description: str

    # The Math Engine
    qty: float
    unit_of_measure: UnitOfMeasureEnum
    unit_price: float
    total_amount: float
    amount_paid: float
    payment_status: StatusEnum

    # Database Links & Context
    entity_name: Optional[str] = Field(default=None)
    reference_tag: Optional[str] = Field(default=None)
    remarks: Optional[str] = Field(default=None)

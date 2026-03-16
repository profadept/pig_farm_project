from typing import Optional
from datetime import date
from enum import Enum
from sqlmodel import SQLModel, Field


class CategoryEnum(str, Enum):
    """The strict VIP list of allowed categories."""

    feed = "Feed"
    medicine = "Medicine"
    sales = "Sales"
    utilities = "Utilities"
    rent = "Rent"
    property = "Property"
    other = "Other"
    labor = "Labor"


class StatusEnum(str, Enum):
    """The strict VIP list of allowed payment statuses."""

    paid = "Paid"
    unpaid = "Unpaid"
    partially_paid = "Partially Paid"


class Transaction(SQLModel, table=True):
    __tablename__ = "farm_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    txn_date: date
    txn_type: str

    # We replaced 'str' with our strict Enums
    category: CategoryEnum
    item_description: str
    qty: float
    unit_price: float
    total_amount: float

    # We replaced 'str' with our strict Enums
    payment_status: StatusEnum
    remarks: Optional[str] = Field(default=None)

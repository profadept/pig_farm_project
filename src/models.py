from enum import Enum
from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

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
    livestock_purchases = "Livestock Purchases"
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
    ml = "ml"
    grams = "grams"


class StatusEnum(str, Enum):
    paid = "Paid"
    unpaid = "Unpaid"
    partially_paid = "Partially Paid"


class UserRole(str, Enum):
    """
    Defines the permission levels for system access.

    """

    ADMIN = "Admin"  # Full access (You)
    STAFF = "Staff"  # Limited access (e.g., can add records, but cannot delete)


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

    user_id: int | None = Field(default=None, foreign_key="users.id")
    
    # 2. The Relationship (The magic Python link)
    user: Optional["User"] = Relationship(back_populates="transactions")


class User(SQLModel, table=True):
    """
    Represents a registered user in the farm management system.

    This table strictly handles authentication (logins) and authorization (roles).
    General farm clients or vendors should NOT be stored in this table
    unless they require direct dashboard access.
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Authentication Core
    username: str = Field(unique=True, index=True)  # <-- Added your username column!
    email: str = Field(unique=True, index=True)
    hashed_password: str

    # Profile & Permissions
    full_name: str
    role: UserRole = Field(default=UserRole.STAFF)
    is_active: bool = Field(default=True)

    transactions: list["Transaction"] = Relationship(back_populates="user")

from enum import Enum
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class TransactionTypeEnum(str, Enum):
    income = "Income"
    expense = "Expense"


class CategoryEnum(str, Enum):
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
    """Defines the permission levels for system access."""

    ADMIN = "Admin"
    STAFF = "Staff"


class SupplyCategoryEnum(str, Enum):
    FEED = "FEED"
    MEDICINE = "MEDICINE"
    EQUIPMENT = "EQUIPMENT"


class UsageMetricEnum(str, Enum):
    BOWLS = "BOWLS"
    ML = "ML"
    KG = "KG"
    GRAMS = "GRAMS"
    LITERS = "LITERS"
    PIECES = "PIECES"


class TrackingTypeEnum(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    BATCH = "BATCH"


class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    MIXED = "MIXED"


class LivestockCategoryEnum(str, Enum):
    PIGLET = "PIGLET"
    WEANER = "WEANER"
    GROWER = "GROWER"
    FATTENER = "FATTENER"
    SOW = "SOW"
    BOAR = "BOAR"


class LivestockStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    PREGNANT = "PREGNANT"
    NURSING = "NURSING"
    SICK = "SICK"
    SOLD = "SOLD"
    DECEASED = "DECEASED"


class LogActionEnum(str, Enum):
    FED = "FED"
    TREATED = "TREATED"
    FARROWED = "FARROWED"
    DIED = "DIED"
    SOLD = "SOLD"
    PROMOTED = "PROMOTED"
    SPLIT = "SPLIT"


class PigBreedEnum(str, Enum):
    LARGE_WHITE = "LARGE_WHITE"
    DUROC = "DUROC"
    LANDRACE = "LANDRACE"
    HAMPSHIRE = "HAMPSHIRE"
    CROSSBREED = "CROSSBREED"
    OTHER = "OTHER"


class Transaction(SQLModel, table=True):
    """The Master Accounting Ledger, Tracks all cash flow in and out of the farm with strict data typing."""

    __tablename__ = "farm_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)

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

    entity_name: Optional[str] = Field(default=None)
    reference_tag: Optional[str] = Field(default=None)
    remarks: Optional[str] = Field(default=None)

    user_id: int | None = Field(default=None, foreign_key="users.id")

    user: Optional["User"] = Relationship(back_populates="transactions")


class User(SQLModel, table=True):
    """
    Represents a registered user in the farm management system.
    This table strictly handles authentication (logins) and authorization (roles).
    General farm clients or vendors should NOT be stored in this table unless they require direct dashboard access.
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    full_name: str
    role: UserRole = Field(default=UserRole.STAFF)
    is_active: bool = Field(default=True)

    transactions: list["Transaction"] = Relationship(back_populates="user")


class SupplyInventory(SQLModel, table=True):
    """The Storehouse for inanimate objects (Feed, Medicine)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    item_name: str
    category: SupplyCategoryEnum

    total_quantity: float = Field(default=0.0)
    unit_of_measure: str

    usage_metric: UsageMetricEnum
    conversion_rate: float = Field(default=1.0)

    logs: list["InventoryLog"] = Relationship(back_populates="supply_used")


class Livestock(SQLModel, table=True):
    """The Animals (Individual tracking or Batches)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_type: TrackingTypeEnum
    identifier: str

    gender: GenderEnum
    breed: PigBreedEnum = Field(default=PigBreedEnum.OTHER)
    category: LivestockCategoryEnum

    quantity: int = Field(default=1)
    status: LivestockStatusEnum = Field(default=LivestockStatusEnum.ACTIVE)
    lineage_note: Optional[str] = None

    logs: list["InventoryLog"] = Relationship(back_populates="livestock")


class InventoryLog(SQLModel, table=True):
    """The Audit Trail (Tracks every action on the farm)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    log_date: datetime = Field(default_factory=datetime.utcnow)
    action_type: LogActionEnum

    supply_used_id: Optional[int] = Field(
        default=None, foreign_key="supplyinventory.id"
    )
    livestock_id: Optional[int] = Field(default=None, foreign_key="livestock.id")

    user_id: int = Field(foreign_key="users.id")

    amount_used: Optional[float] = None
    remarks: Optional[str] = None

    supply_used: Optional[SupplyInventory] = Relationship(back_populates="logs")
    livestock: Optional[Livestock] = Relationship(back_populates="logs")

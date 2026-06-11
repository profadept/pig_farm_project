from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel


class SupplyCategoryEnum(StrEnum):
    FEED = "FEED"
    MEDICINE = "MEDICINE"
    EQUIPMENT = "EQUIPMENT"


class UsageMetricEnum(StrEnum):
    BOWLS = "BOWLS"
    ML = "ML"
    KG = "KG"
    GRAMS = "GRAMS"
    LITERS = "LITERS"
    PIECES = "PIECES"


class SupplyInventory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    item_name: str
    category: SupplyCategoryEnum

    total_quantity: float = Field(default=0.0)
    unit_of_measure: str

    usage_metric: UsageMetricEnum
    conversion_rate: float = Field(default=1.0)

    logs: list["InventoryLog"] = Relationship(back_populates="supply_used")  # noqa: F821

from datetime import UTC, datetime
from enum import StrEnum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class LogActionEnum(StrEnum):
    FED = "FED"
    TREATED = "TREATED"
    FARROWED = "FARROWED"
    DIED = "DIED"
    SOLD = "SOLD"
    PROMOTED = "PROMOTED"
    SPLIT = "SPLIT"


class InventoryLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    log_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    action_type: LogActionEnum

    amount_used: float | None = None
    remarks: str | None = None

    supply_used_id: int | None = Field(default=None, foreign_key="supplyinventory.id")
    livestock_id: int | None = Field(default=None, foreign_key="livestock.id")
    user_id: int = Field(foreign_key="users.id")

    supply_used: Optional["SupplyInventory"] = Relationship(back_populates="logs")  # noqa: F821
    livestock: Optional["Livestock"] = Relationship(back_populates="logs")  # noqa: F821

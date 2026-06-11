from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel


class TrackingTypeEnum(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"
    BATCH = "BATCH"


class GenderEnum(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    MIXED = "MIXED"


class PigBreedEnum(StrEnum):
    LARGE_WHITE = "LARGE_WHITE"
    DUROC = "DUROC"
    LANDRACE = "LANDRACE"
    HAMPSHIRE = "HAMPSHIRE"
    CROSSBREED = "CROSSBREED"
    OTHER = "OTHER"


class LivestockStatusEnum(StrEnum):
    ACTIVE = "ACTIVE"
    PREGNANT = "PREGNANT"
    NURSING = "NURSING"
    SICK = "SICK"
    SOLD = "SOLD"
    DECEASED = "DECEASED"


class LivestockCategoryEnum(StrEnum):
    PIGLET = "PIGLET"
    WEANER = "WEANER"
    GROWER = "GROWER"
    FATTENER = "FATTENER"
    SOW = "SOW"
    BOAR = "BOAR"


class Livestock(SQLModel, table=True):
    """Vault 2: The Animals (Individual tracking or Batches)."""

    id: int | None = Field(default=None, primary_key=True)

    tracking_type: TrackingTypeEnum
    identifier: str

    gender: GenderEnum
    breed: PigBreedEnum = Field(default=PigBreedEnum.OTHER)
    category: LivestockCategoryEnum

    quantity: int = Field(default=1)
    status: LivestockStatusEnum = Field(default=LivestockStatusEnum.ACTIVE)
    lineage_note: str | None = None

    logs: list["InventoryLog"] = Relationship(back_populates="livestock")  # noqa: F821

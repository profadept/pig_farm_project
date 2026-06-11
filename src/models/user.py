from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel


class UserRole(StrEnum):
    """
    Defines the permission levels for system access.
    """

    ADMIN = "Admin"
    STAFF = "Staff"


class User(SQLModel, table=True):
    """
    Represents a registered user in the farm management system.

    This table strictly handles authentication (logins) and authorization (roles).
    General farm clients or vendors should NOT be stored in this table
    unless they require direct dashboard access.
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    full_name: str
    role: UserRole = Field(default=UserRole.STAFF)
    is_active: bool = Field(default=True)

    transactions: list["Transaction"] = Relationship(back_populates="user")  # noqa: F821

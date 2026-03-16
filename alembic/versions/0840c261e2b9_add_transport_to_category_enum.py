"""add transport to category enum

Revision ID: 0840c261e2b9
Revises: e403293e8e87
Create Date: 2026-03-16 18:10:15.180503

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0840c261e2b9"
down_revision: Union[str, Sequence[str], None] = "e403293e8e87"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def upgrade() -> None:
    # We use raw SQL to forcefully inject the new VIP word into PostgreSQL
    op.execute("ALTER TYPE categoryenum ADD VALUE 'Transport'")


def downgrade() -> None:
    # Postgres does not easily let you delete Enum values once added, so we pass
    pass

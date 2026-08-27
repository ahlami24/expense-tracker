"""add notes to expenses

Revision ID: 091d8d2d9427
Revises: ad420541ee7c
Create Date: 2026-08-23 09:14:23.147063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '091d8d2d9427'
down_revision: Union[str, Sequence[str], None] = 'ad420541ee7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "expenses",
        sa.Column("notes", sa.Text(), nullable=True)
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("expenses", "notes")

"""add viewer role

Revision ID: 26168d08af4b
Revises: 001_initial
Create Date: 2026-08-25 12:34:43.767378
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '26168d08af4b'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use autocommit to execute ALTER TYPE because it cannot run in a transaction block
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'viewer'")

def downgrade() -> None:
    # Cannot remove a value from an enum easily in postgres, so do nothing.
    pass

"""make_current_hash_nullable

Revision ID: a8ec89527ceb
Revises: 3a3da1f4f764
Create Date: 2025-11-04 21:30:37.077039

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8ec89527ceb"
down_revision: Union[str, Sequence[str], None] = "3a3da1f4f764"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make current_hash nullable
    op.alter_column("audit_chains", "current_hash", nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make current_hash not nullable again
    op.alter_column("audit_chains", "current_hash", nullable=False)

"""add_trust_score_to_users

Revision ID: a24444214bd9
Revises: 01c8b8690a57
Create Date: 2025-11-04 14:53:22.154165

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a24444214bd9"
down_revision: Union[str, Sequence[str], None] = "01c8b8690a57"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add trust_score column to users table
    op.add_column(
        "users",
        sa.Column("trust_score", sa.Integer(), nullable=False, server_default="100"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove trust_score column from users table
    op.drop_column("users", "trust_score")

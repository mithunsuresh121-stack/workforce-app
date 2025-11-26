"""add_fcm_token_to_users

Revision ID: 20d2cfecf869
Revises: 397e81441b50
Create Date: 2025-10-23 15:52:02.037059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20d2cfecf869'
down_revision: Union[str, Sequence[str], None] = '397e81441b50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add fcm_token column to users table
    op.add_column('users', sa.Column('fcm_token', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove fcm_token column from users table
    op.drop_column('users', 'fcm_token')

"""merge_heads

Revision ID: 8bee06c32eee
Revises: 0008, add_timestamps
Create Date: 2025-10-23 12:14:44.033969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bee06c32eee'
down_revision: Union[str, Sequence[str], None] = ('0008', 'add_timestamps')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

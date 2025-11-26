"""merge_heads_before_org

Revision ID: 17329d64debb
Revises: 7c5fb8a8d933, company_bootstrap_001
Create Date: 2025-11-03 09:52:24.622491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17329d64debb'
down_revision: Union[str, Sequence[str], None] = ('7c5fb8a8d933', 'company_bootstrap_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

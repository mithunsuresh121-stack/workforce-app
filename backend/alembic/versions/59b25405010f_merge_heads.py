"""merge heads

Revision ID: 59b25405010f
Revises: add_documents_table_final, phase2_attendance_leave_updates
Create Date: 2025-10-02 18:39:04.458473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59b25405010f'
down_revision: Union[str, Sequence[str], None] = ('add_documents_table_final', 'phase2_attendance_leave_updates')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

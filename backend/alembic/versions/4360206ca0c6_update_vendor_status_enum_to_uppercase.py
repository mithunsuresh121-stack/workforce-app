"""update vendor_status enum to uppercase

Revision ID: 4360206ca0c6
Revises: cec574960b1c
Create Date: 2025-11-10 20:18:05.614290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4360206ca0c6'
down_revision: Union[str, Sequence[str], None] = 'cec574960b1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old enum
    op.execute("DROP TYPE vendor_status CASCADE")
    # Create the new enum with uppercase values
    op.execute("CREATE TYPE vendor_status AS ENUM('ACTIVE', 'INACTIVE')")
    # Add the columns back
    op.add_column('vendors', sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', name='vendor_status'), default='ACTIVE'))
    op.add_column('vendors', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')))


def downgrade() -> None:
    """Downgrade schema."""
    pass

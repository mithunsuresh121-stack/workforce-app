"""update purchase_order_status enum to uppercase

Revision ID: cec574960b1c
Revises: 541bcdf11be4
Create Date: 2025-11-10 20:10:26.432048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cec574960b1c'
down_revision: Union[str, Sequence[str], None] = '541bcdf11be4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old enum
    op.execute("DROP TYPE purchase_order_status CASCADE")
    # Create the new enum with uppercase values
    op.execute("CREATE TYPE purchase_order_status AS ENUM('PENDING', 'APPROVED', 'REJECTED', 'COMPLETED')")
    # Add the columns back
    op.add_column('purchase_orders', sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'COMPLETED', name='purchase_order_status'), default='PENDING'))
    op.add_column('purchase_orders', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')))


def downgrade() -> None:
    """Downgrade schema."""
    pass

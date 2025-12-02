"""Add created_at and updated_at columns to leaves and shifts tables

Revision ID: add_timestamps
Revises: 0003
Create Date: 2025-09-03 14:46:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.sql import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_timestamps"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    # Add created_at and updated_at columns to leaves table
    op.add_column(
        "leaves",
        sa.Column("created_at", sa.DateTime(), nullable=True, default=func.now()),
    )
    op.add_column(
        "leaves",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Add created_at and updated_at columns to shifts table
    op.add_column(
        "shifts",
        sa.Column("created_at", sa.DateTime(), nullable=True, default=func.now()),
    )
    op.add_column(
        "shifts",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Set default values for existing records
    op.execute(
        "UPDATE leaves SET created_at = NOW(), updated_at = NOW() WHERE created_at IS NULL"
    )
    op.execute(
        "UPDATE shifts SET created_at = NOW(), updated_at = NOW() WHERE created_at IS NULL"
    )

    # Make columns non-nullable after setting defaults
    op.alter_column("leaves", "created_at", nullable=False)
    op.alter_column("leaves", "updated_at", nullable=False)
    op.alter_column("shifts", "created_at", nullable=False)
    op.alter_column("shifts", "updated_at", nullable=False)


def downgrade():
    # Remove the columns
    op.drop_column("shifts", "updated_at")
    op.drop_column("shifts", "created_at")
    op.drop_column("leaves", "updated_at")
    op.drop_column("leaves", "created_at")

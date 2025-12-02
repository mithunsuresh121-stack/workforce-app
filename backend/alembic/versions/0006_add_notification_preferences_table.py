"""Add notification preferences table

Revision ID: 0006
Revises: 0005
Create Date: 2025-01-06 21:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_preferences table
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        op.f("ix_notification_preferences_id"),
        "notification_preferences",
        ["id"],
        unique=False,
    )


def downgrade():
    # Drop notification_preferences table
    op.drop_index(
        op.f("ix_notification_preferences_id"), table_name="notification_preferences"
    )
    op.drop_table("notification_preferences")

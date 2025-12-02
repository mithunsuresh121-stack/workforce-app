"""Add notification digest table and update preferences

Revision ID: 0007
Revises: 0006
Create Date: 2025-01-06 21:30:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_digests table
    op.create_table(
        "notification_digests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "digest_type", sa.Enum("DAILY", "WEEKLY", name="digesttype"), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "SENT", "FAILED", name="digeststatus"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("notification_count", sa.Integer(), nullable=False),
        sa.Column("notification_ids", sa.JSON(), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notification_digests_id"), "notification_digests", ["id"], unique=False
    )

    # Add new columns to notification_preferences table (nullable first)
    op.add_column(
        "notification_preferences", sa.Column("mute_all", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "notification_preferences",
        sa.Column("digest_mode", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "notification_preferences",
        sa.Column("push_enabled", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "notification_preferences",
        sa.Column("notification_types", sa.JSON(), nullable=True),
    )

    # Update existing records with default values
    op.execute(
        "UPDATE notification_preferences SET mute_all = false WHERE mute_all IS NULL"
    )
    op.execute(
        "UPDATE notification_preferences SET digest_mode = 'immediate' WHERE digest_mode IS NULL"
    )
    op.execute(
        "UPDATE notification_preferences SET push_enabled = true WHERE push_enabled IS NULL"
    )
    op.execute(
        'UPDATE notification_preferences SET notification_types = \'{"TASK_ASSIGNED": true, "SHIFT_SCHEDULED": true, "SYSTEM_MESSAGE": true, "ADMIN_MESSAGE": true}\' WHERE notification_types IS NULL'
    )

    # Now make columns NOT NULL
    op.alter_column("notification_preferences", "mute_all", nullable=False)
    op.alter_column("notification_preferences", "digest_mode", nullable=False)
    op.alter_column("notification_preferences", "push_enabled", nullable=False)
    op.alter_column("notification_preferences", "notification_types", nullable=False)

    # Remove the old preferences column
    op.drop_column("notification_preferences", "preferences")


def downgrade():
    # Add back the preferences column
    op.add_column(
        "notification_preferences", sa.Column("preferences", sa.JSON(), nullable=True)
    )

    # Remove new columns
    op.drop_column("notification_preferences", "notification_types")
    op.drop_column("notification_preferences", "push_enabled")
    op.drop_column("notification_preferences", "digest_mode")
    op.drop_column("notification_preferences", "mute_all")

    # Drop notification_digests table
    op.drop_index(op.f("ix_notification_digests_id"), table_name="notification_digests")
    op.drop_table("notification_digests")

"""Update tasks table with new fields

Revision ID: 0005
Revises: 0004
Create Date: 2025-09-05 19:50:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column("tasks", sa.Column("assigned_by", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("priority", sa.String(), nullable=True))

    # Create foreign key constraint for assigned_by
    op.create_foreign_key(
        "fk_tasks_assigned_by", "tasks", "users", ["assigned_by"], ["id"]
    )

    # Update existing records to have default priority
    op.execute("UPDATE tasks SET priority = 'Medium' WHERE priority IS NULL")

    # Make priority non-nullable
    op.alter_column("tasks", "priority", nullable=False)

    # 1. Change column type to text temporarily
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE TEXT")

    # 2. Update existing values while status is TEXT
    op.execute("UPDATE tasks SET status = 'Pending' WHERE status = 'TODO'")
    op.execute("UPDATE tasks SET status = 'In Progress' WHERE status = 'IN_PROGRESS'")
    op.execute("UPDATE tasks SET status = 'Completed' WHERE status = 'DONE'")

    # 3. Drop existing enum type
    op.execute("DROP TYPE IF EXISTS taskstatus CASCADE")

    # 4. Create new enum with correct values
    op.execute(
        "CREATE TYPE taskstatus AS ENUM('Pending', 'In Progress', 'Completed', 'Overdue')"
    )

    # 5. Cast column to new enum type
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus USING status::taskstatus"
    )


def downgrade():
    # Revert the enum changes
    op.execute("ALTER TYPE taskstatus RENAME TO taskstatus_old")
    op.execute("CREATE TYPE taskstatus AS ENUM('TODO', 'IN_PROGRESS', 'DONE')")

    # Update status values back
    op.execute("UPDATE tasks SET status = 'TODO' WHERE status = 'Pending'")
    op.execute("UPDATE tasks SET status = 'IN_PROGRESS' WHERE status = 'In Progress'")
    op.execute("UPDATE tasks SET status = 'DONE' WHERE status = 'Completed'")

    # Change the column type back
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus USING status::text::taskstatus"
    )

    # Drop the new enum and rename old back
    op.execute("DROP TYPE taskstatus_old")

    # Remove the new columns
    op.drop_constraint("fk_tasks_assigned_by", "tasks", type_="foreignkey")
    op.drop_column("tasks", "priority")
    op.drop_column("tasks", "assigned_by")

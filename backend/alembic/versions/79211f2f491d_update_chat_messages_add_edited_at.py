"""update_chat_messages_add_edited_at

Revision ID: 79211f2f491d
Revises: 9e426941daf4
Create Date: 2025-10-28 14:13:30.634357

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "79211f2f491d"
down_revision: Union[str, Sequence[str], None] = "9e426941daf4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add edited_at column to chat_messages
    op.add_column(
        "chat_messages",
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop edited_at column from chat_messages
    op.drop_column("chat_messages", "edited_at")

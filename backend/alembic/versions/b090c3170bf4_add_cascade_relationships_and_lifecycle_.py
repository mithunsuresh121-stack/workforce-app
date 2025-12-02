"""add_cascade_relationships_and_lifecycle_fields

Revision ID: b090c3170bf4
Revises: 79211f2f491d
Create Date: 2025-10-30 20:01:33.258274

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b090c3170bf4"
down_revision: Union[str, Sequence[str], None] = "79211f2f491d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add lifecycle audit fields
    op.add_column(
        "channels", sa.Column("last_message_at", sa.DateTime(), nullable=True)
    )
    op.add_column("users", sa.Column("last_active", sa.DateTime(), nullable=True))

    # Add CASCADE constraints to existing foreign keys
    # Note: Alembic doesn't auto-detect relationship changes, so we need to manually add CASCADE
    # For PostgreSQL, CASCADE is added via ALTER TABLE ALTER CONSTRAINT
    # But since the FKs already exist, we need to drop and recreate them with CASCADE

    # Channels table FKs
    op.drop_constraint("channels_company_id_fkey", "channels", type_="foreignkey")
    op.create_foreign_key(
        "channels_company_id_fkey",
        "channels",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("channels_created_by_fkey", "channels", type_="foreignkey")
    op.create_foreign_key(
        "channels_created_by_fkey",
        "channels",
        "users",
        ["created_by"],
        ["id"],
        ondelete="CASCADE",
    )

    # Channel members table FKs
    op.drop_constraint(
        "channel_members_channel_id_fkey", "channel_members", type_="foreignkey"
    )
    op.create_foreign_key(
        "channel_members_channel_id_fkey",
        "channel_members",
        "channels",
        ["channel_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "channel_members_user_id_fkey", "channel_members", type_="foreignkey"
    )
    op.create_foreign_key(
        "channel_members_user_id_fkey",
        "channel_members",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Chat messages table FKs
    op.drop_constraint(
        "chat_messages_company_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_company_id_fkey",
        "chat_messages",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "chat_messages_sender_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_sender_id_fkey",
        "chat_messages",
        "users",
        ["sender_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "chat_messages_receiver_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_receiver_id_fkey",
        "chat_messages",
        "users",
        ["receiver_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "chat_messages_channel_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_channel_id_fkey",
        "chat_messages",
        "channels",
        ["channel_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Message reactions table FKs
    op.drop_constraint(
        "message_reactions_message_id_fkey", "message_reactions", type_="foreignkey"
    )
    op.create_foreign_key(
        "message_reactions_message_id_fkey",
        "message_reactions",
        "chat_messages",
        ["message_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "message_reactions_user_id_fkey", "message_reactions", type_="foreignkey"
    )
    op.create_foreign_key(
        "message_reactions_user_id_fkey",
        "message_reactions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Meetings table FKs
    op.drop_constraint("meetings_company_id_fkey", "meetings", type_="foreignkey")
    op.create_foreign_key(
        "meetings_company_id_fkey",
        "meetings",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("meetings_organizer_id_fkey", "meetings", type_="foreignkey")
    op.create_foreign_key(
        "meetings_organizer_id_fkey",
        "meetings",
        "users",
        ["organizer_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Meeting participants table FKs
    op.drop_constraint(
        "meeting_participants_meeting_id_fkey",
        "meeting_participants",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "meeting_participants_meeting_id_fkey",
        "meeting_participants",
        "meetings",
        ["meeting_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "meeting_participants_user_id_fkey", "meeting_participants", type_="foreignkey"
    )
    op.create_foreign_key(
        "meeting_participants_user_id_fkey",
        "meeting_participants",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Users table FK (company_id)
    op.drop_constraint("users_company_id_fkey", "users", type_="foreignkey")
    op.create_foreign_key(
        "users_company_id_fkey",
        "users",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove CASCADE constraints and revert to NO ACTION
    # Users table FK (company_id)
    op.drop_constraint("users_company_id_fkey", "users", type_="foreignkey")
    op.create_foreign_key(
        "users_company_id_fkey", "users", "companies", ["company_id"], ["id"]
    )

    # Meeting participants table FKs
    op.drop_constraint(
        "meeting_participants_user_id_fkey", "meeting_participants", type_="foreignkey"
    )
    op.create_foreign_key(
        "meeting_participants_user_id_fkey",
        "meeting_participants",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_constraint(
        "meeting_participants_meeting_id_fkey",
        "meeting_participants",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "meeting_participants_meeting_id_fkey",
        "meeting_participants",
        "meetings",
        ["meeting_id"],
        ["id"],
    )

    # Meetings table FKs
    op.drop_constraint("meetings_organizer_id_fkey", "meetings", type_="foreignkey")
    op.create_foreign_key(
        "meetings_organizer_id_fkey", "meetings", "users", ["organizer_id"], ["id"]
    )

    op.drop_constraint("meetings_company_id_fkey", "meetings", type_="foreignkey")
    op.create_foreign_key(
        "meetings_company_id_fkey", "meetings", "companies", ["company_id"], ["id"]
    )

    # Message reactions table FKs
    op.drop_constraint(
        "message_reactions_user_id_fkey", "message_reactions", type_="foreignkey"
    )
    op.create_foreign_key(
        "message_reactions_user_id_fkey",
        "message_reactions",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_constraint(
        "message_reactions_message_id_fkey", "message_reactions", type_="foreignkey"
    )
    op.create_foreign_key(
        "message_reactions_message_id_fkey",
        "message_reactions",
        "chat_messages",
        ["message_id"],
        ["id"],
    )

    # Chat messages table FKs
    op.drop_constraint(
        "chat_messages_channel_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_channel_id_fkey",
        "chat_messages",
        "channels",
        ["channel_id"],
        ["id"],
    )

    op.drop_constraint(
        "chat_messages_receiver_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_receiver_id_fkey",
        "chat_messages",
        "users",
        ["receiver_id"],
        ["id"],
    )

    op.drop_constraint(
        "chat_messages_sender_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_sender_id_fkey", "chat_messages", "users", ["sender_id"], ["id"]
    )

    op.drop_constraint(
        "chat_messages_company_id_fkey", "chat_messages", type_="foreignkey"
    )
    op.create_foreign_key(
        "chat_messages_company_id_fkey",
        "chat_messages",
        "companies",
        ["company_id"],
        ["id"],
    )

    # Channel members table FKs
    op.drop_constraint(
        "channel_members_user_id_fkey", "channel_members", type_="foreignkey"
    )
    op.create_foreign_key(
        "channel_members_user_id_fkey", "channel_members", "users", ["user_id"], ["id"]
    )

    op.drop_constraint(
        "channel_members_channel_id_fkey", "channel_members", type_="foreignkey"
    )
    op.create_foreign_key(
        "channel_members_channel_id_fkey",
        "channel_members",
        "channels",
        ["channel_id"],
        ["id"],
    )

    # Channels table FKs
    op.drop_constraint("channels_created_by_fkey", "channels", type_="foreignkey")
    op.create_foreign_key(
        "channels_created_by_fkey", "channels", "users", ["created_by"], ["id"]
    )

    op.drop_constraint("channels_company_id_fkey", "channels", type_="foreignkey")
    op.create_foreign_key(
        "channels_company_id_fkey", "channels", "companies", ["company_id"], ["id"]
    )

    # Remove lifecycle audit fields
    op.drop_column("users", "last_active")
    op.drop_column("channels", "last_message_at")

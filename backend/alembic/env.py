import os
import sys

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.db import Base
from app.models import (channels, chat, company, leave,  # noqa
                        meeting_participants, meetings, message_reactions,
                        profile_update_request, shift, task, user)

config = context.config

target_metadata = Base.metadata


def run_migrations_offline():
    url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
    connectable = engine_from_config(
        {}, prefix="sqlalchemy.", poolclass=pool.NullPool, url=url
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

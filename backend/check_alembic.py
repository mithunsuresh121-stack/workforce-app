from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version')).fetchone()
    print(result[0] if result else 'No version found')

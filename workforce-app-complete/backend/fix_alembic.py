#!/usr/bin/env python3
"""
Fix alembic version to 0007
"""

from app.db import engine
from sqlalchemy import text

def fix_alembic():
    with engine.connect() as conn:
        conn.execute(text("UPDATE alembic_version SET version_num = '0007'"))
        conn.commit()
        print("✅ Alembic version set to 0007")

if __name__ == "__main__":
    fix_alembic()

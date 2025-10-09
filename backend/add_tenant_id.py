from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE leaves ADD COLUMN IF NOT EXISTS tenant_id VARCHAR NOT NULL DEFAULT '1'"))
    conn.commit()
    print('tenant_id column added')

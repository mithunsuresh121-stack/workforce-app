from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS leaves (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            employee_id INTEGER NOT NULL REFERENCES users(id),
            type VARCHAR NOT NULL,
            start_at TIMESTAMP NOT NULL,
            end_at TIMESTAMP NOT NULL,
            status VARCHAR DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT now(),
            updated_at TIMESTAMP DEFAULT now()
        )
    """))
    conn.commit()
    print("Leaves table created")

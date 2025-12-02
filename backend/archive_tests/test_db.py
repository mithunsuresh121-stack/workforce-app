from sqlalchemy import text

from app.db import engine

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")

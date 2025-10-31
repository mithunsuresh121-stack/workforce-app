#!/usr/bin/env python3
"""
Reset the database by dropping and recreating the public schema.
"""
from app.db import engine
from sqlalchemy import text

def reset_database():
    with engine.connect() as conn:
        # Drop and recreate the public schema
        conn.execute(text('DROP SCHEMA public CASCADE'))
        conn.execute(text('CREATE SCHEMA public'))
        conn.commit()
        print('Database reset successfully')

if __name__ == "__main__":
    reset_database()

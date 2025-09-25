#!/usr/bin/env python3
"""
Migration script to add logo_url column to companies table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import DATABASE_URL

def add_logo_url_column():
    """Add logo_url column to companies table"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)

        # Add the logo_url column
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'companies' AND column_name = 'logo_url'
            """))

            if not result.fetchone():
                print("Adding logo_url column to companies table...")
                conn.execute(text("ALTER TABLE companies ADD COLUMN logo_url VARCHAR"))
                conn.commit()
                print("✓ Successfully added logo_url column")
            else:
                print("✓ logo_url column already exists")

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_logo_url_column()

#!/usr/bin/env python3
"""
Simple script to create employee profiles for existing demo users.
This script uses raw SQL to avoid import issues.
"""

import psycopg2
from datetime import datetime

def main():
    print("Creating employee profiles for demo users...")

    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="workforce",
            user="workforce",
            password="workforce_pw",
            port="5432"
        )

        cursor = conn.cursor()

        # Get existing users and company
        cursor.execute("SELECT id, email FROM users WHERE email IN ('admin@app.com', 'demo@company.com')")
        users = cursor.fetchall()

        cursor.execute("SELECT id FROM companies WHERE name = 'Demo Company'")
        company_result = cursor.fetchone()

        if not company_result:
            print("Demo company not found!")
            return

        company_id = company_result[0]

        print(f"Found {len(users)} users and company ID {company_id}")

        # Create employee profiles
        for user_id, email in users:
            # Check if profile already exists
            cursor.execute("SELECT id FROM employee_profiles WHERE user_id = %s", (user_id,))
            existing = cursor.fetchone()

            if existing:
                print(f"Profile already exists for {email}")
                continue

            # Create profile
            if email == "admin@app.com":
                cursor.execute("""
                    INSERT INTO employee_profiles
                    (user_id, company_id, department, position, phone, hire_date, is_active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, company_id, "IT", "System Administrator", "+1234567890", "2023-01-01", True, datetime.now(), datetime.now()))
                print("Created employee profile for Super Admin")
            else:
                cursor.execute("""
                    INSERT INTO employee_profiles
                    (user_id, company_id, department, position, phone, hire_date, is_active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, company_id, "Engineering", "Software Engineer", "+1234567891", "2023-06-01", True, datetime.now(), datetime.now()))
                print("Created employee profile for Demo User")

        conn.commit()
        print("Employee profiles created successfully!")

    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()

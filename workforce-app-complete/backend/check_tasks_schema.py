from app.db import engine
from sqlalchemy import text

def check_tasks_schema():
    with engine.connect() as conn:
        # Check table schema
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tasks' ORDER BY ordinal_position;"))
        print("Tasks table schema:")
        for row in result:
            print(f"{row[0]}: {row[1]}")

        # Check actual data
        result = conn.execute(text("SELECT id, title, status, company_id, assigned_by, assignee_id, priority FROM tasks LIMIT 5;"))
        print("\nTasks data (first 5 rows):")
        for row in result:
            print(f"ID: {row[0]}, Title: {row[1]}, Status: {row[2]}, Company: {row[3]}, Assigned By: {row[4]}, Assignee: {row[5]}, Priority: {row[6]}")

if __name__ == "__main__":
    check_tasks_schema()

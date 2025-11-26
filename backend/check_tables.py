from app.db import engine
from sqlalchemy import text

def check_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
        tables = [row[0] for row in result.fetchall()]
        print("Tables in database:", tables)

        # Check specifically for notification_preferences
        if 'notification_preferences' in tables:
            print("notification_preferences table exists")
        else:
            print("notification_preferences table does NOT exist")

if __name__ == "__main__":
    check_tables()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.models.user import User
from app.models.notification_preferences import NotificationPreferences, DigestMode
from app.crud_notification_preferences import create_user_preferences
from structlog import get_logger

logger = get_logger()

def create_notification_preferences_table():
    """Create the notification_preferences table if it doesn't exist"""
    with engine.connect() as conn:
        # Check if table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'notification_preferences'
            );
        """))
        exists = result.scalar()
        
        if exists:
            logger.info("notification_preferences table already exists")
            return
        
        logger.info("Creating notification_preferences table")
        
        # Create table with final structure from migration 0007
        conn.execute(text("""
            CREATE TABLE notification_preferences (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                company_id INTEGER NOT NULL,
                mute_all BOOLEAN NOT NULL DEFAULT false,
                digest_mode VARCHAR(20) NOT NULL DEFAULT 'immediate',
                push_enabled BOOLEAN NOT NULL DEFAULT true,
                notification_types JSON NOT NULL DEFAULT '{"TASK_ASSIGNED": true, "SHIFT_SCHEDULED": true, "SYSTEM_MESSAGE": true, "ADMIN_MESSAGE": true}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            );
            
            CREATE INDEX ix_notification_preferences_user_id ON notification_preferences (user_id);
            CREATE INDEX ix_notification_preferences_company_id ON notification_preferences (company_id);
        """))
        conn.commit()
        logger.info("notification_preferences table created successfully")

def populate_default_preferences():
    """Create default preferences for existing users without preferences"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get users without preferences
        users_without_prefs = db.query(User).outerjoin(NotificationPreferences, User.id == NotificationPreferences.user_id).filter(NotificationPreferences.id.is_(None)).all()
        
        for user in users_without_prefs:
            if user.company_id:
                create_user_preferences(
                    db, 
                    user_id=user.id, 
                    company_id=user.company_id,
                    preferences={
                        "mute_all": False,
                        "digest_mode": DigestMode.IMMEDIATE,
                        "push_enabled": True,
                        "notification_types": {
                            "TASK_ASSIGNED": True,
                            "SHIFT_SCHEDULED": True,
                            "SYSTEM_MESSAGE": True,
                            "ADMIN_MESSAGE": True
                        }
                    }
                )
                logger.info(f"Created default preferences for user {user.id}")
        
        db.commit()
        logger.info(f"Populated default preferences for {len(users_without_prefs)} users")
    
    except Exception as e:
        logger.error(f"Error populating default preferences: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_notification_preferences_table()
    populate_default_preferences()
    print("Notification preferences setup completed")

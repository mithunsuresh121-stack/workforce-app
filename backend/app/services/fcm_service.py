import structlog
import firebase_admin
from firebase_admin import messaging, credentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os

logger = structlog.get_logger(__name__)

class FCMService:
    def __init__(self):
        self._initialized = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if firebase_admin._apps:
                self._initialized = True
                return

            # Try to get credentials from environment or file
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for GCP environments)
                firebase_admin.initialize_app()

            self._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            self._initialized = False

    def send_push_notification(self, token: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> bool:
        """
        Send a push notification to a specific FCM token
        """
        if not self._initialized:
            logger.error("Firebase not initialized, cannot send push notification")
            return False

        if not token:
            logger.warning("No FCM token provided for push notification")
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )

            response = messaging.send(message)
            logger.info(f"Push notification sent successfully: {response}")
            return True

        except messaging.UnregisteredError:
            logger.warning(f"FCM token is unregistered: {token}")
            return False
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False

    def send_multicast_notification(self, tokens: list, title: str, body: str, data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send push notification to multiple tokens
        """
        if not self._initialized:
            logger.error("Firebase not initialized, cannot send multicast notification")
            return {"success": 0, "failure": len(tokens)}

        if not tokens:
            logger.warning("No FCM tokens provided for multicast notification")
            return {"success": 0, "failure": 0}

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )

            response = messaging.send_multicast(message)
            success_count = response.success_count
            failure_count = response.failure_count

            logger.info(f"Multicast notification sent: {success_count} success, {failure_count} failure")

            # Log failures for debugging
            if response.responses:
                for i, resp in enumerate(response.responses):
                    if not resp.success:
                        logger.warning(f"Failed to send to token {i}: {resp.exception}")

            return {
                "success": success_count,
                "failure": failure_count,
                "total": len(tokens)
            }

        except Exception as e:
            logger.error(f"Failed to send multicast notification: {str(e)}")
            return {"success": 0, "failure": len(tokens), "error": str(e)}

    def update_user_fcm_token(self, db: Session, user_id: int, fcm_token: str) -> bool:
        """
        Update FCM token for a user
        """
        try:
            from ..models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.fcm_token = fcm_token
                db.commit()
                logger.info(f"Updated FCM token for user {user_id}")
                return True
            else:
                logger.warning(f"User {user_id} not found for FCM token update")
                return False
        except Exception as e:
            logger.error(f"Failed to update FCM token for user {user_id}: {str(e)}")
            db.rollback()
            return False

    def get_user_fcm_token(self, db: Session, user_id: int) -> Optional[str]:
        """
        Get FCM token for a user
        """
        try:
            from ..models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            return user.fcm_token if user else None
        except Exception as e:
            logger.error(f"Failed to get FCM token for user {user_id}: {str(e)}")
            return None

# Global FCM service instance
fcm_service = FCMService()

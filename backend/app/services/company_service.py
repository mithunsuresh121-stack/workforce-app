import structlog
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import string
from passlib.context import CryptContext

from app.models.company import Company
from app.models.company_settings import CompanySettings
from app.models.user import User
from app.models.channels import Channel, ChannelType, ChannelMember
from app.models.meetings import Meeting, MeetingStatus
from app.models.meeting_participants import MeetingParticipant, ParticipantRole
from app.models.audit_log import AuditLog
from app.services.audit_service import AuditService
from app.metrics import company_created_total, company_admin_created_total
from app.base_crud import create_user

logger = structlog.get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CompanyService:
    @staticmethod
    def bootstrap_company(
        db: Session,
        company_name: str,
        superadmin_user: User
    ) -> Dict[str, Any]:
        """
        Bootstrap a new company with all required components.
        Returns company, first_admin_user, and bootstrap_status.
        """
        if superadmin_user.role != "SUPERADMIN":
            raise ValueError("Only SUPERADMIN can bootstrap companies")

        # Start transaction
        try:
            # 1. Create company
            company = Company(name=company_name)
            db.add(company)
            db.flush()  # Get company ID

            # 2. Create first CompanyAdmin user
            admin_email = f"admin@{company_name.lower().replace(' ', '')}.com"
            temp_password = CompanyService._generate_temp_password()
            hashed_password = pwd_context.hash(temp_password)

            admin_user = User(
                email=admin_email,
                hashed_password=hashed_password,
                full_name=f"{company_name} Admin",
                role="COMPANYADMIN",
                company_id=company.id
            )
            db.add(admin_user)
            db.flush()

            # 3. Create default "General" channel
            general_channel = Channel(
                name="General",
                type=ChannelType.PUBLIC,
                company_id=company.id,
                created_by=admin_user.id
            )
            db.add(general_channel)
            db.flush()

            # Add admin to General channel
            channel_member = ChannelMember(
                channel_id=general_channel.id,
                user_id=admin_user.id
            )
            db.add(channel_member)

            # 4. Create default "Meeting Room"
            meeting_room = Meeting(
                title="Meeting Room",
                organizer_id=admin_user.id,
                company_id=company.id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(hours=1),
                status=MeetingStatus.SCHEDULED
            )
            db.add(meeting_room)
            db.flush()

            # Add admin as organizer
            meeting_participant = MeetingParticipant(
                meeting_id=meeting_room.id,
                user_id=admin_user.id,
                role=ParticipantRole.ORGANIZER
            )
            db.add(meeting_participant)

            # 5. Create company settings
            company_settings = CompanySettings(company_id=company.id)
            db.add(company_settings)

            # 6. Log audit event
            AuditService.log_company_bootstrapped(
                db=db,
                user_id=superadmin_user.id,
                company_id=company.id,
                details={
                    "admin_user_id": admin_user.id,
                    "general_channel_id": general_channel.id,
                    "meeting_room_id": meeting_room.id,
                    "settings_id": company_settings.id
                }
            )

            # 7. Increment metrics
            company_created_total.inc()
            company_admin_created_total.inc()

            # Commit transaction
            db.commit()

            # Refresh objects
            db.refresh(company)
            db.refresh(admin_user)
            db.refresh(general_channel)
            db.refresh(meeting_room)
            db.refresh(company_settings)

            # Generate temporary access token/link (24h expiry)
            temp_token = CompanyService._generate_temp_token()
            expiry_time = datetime.utcnow() + timedelta(hours=24)

            logger.info(
                "Company bootstrapped successfully",
                company_id=company.id,
                admin_user_id=admin_user.id,
                superadmin_id=superadmin_user.id
            )

            return {
                "company": company,
                "first_admin_user": admin_user,
                "bootstrap_status": "success",
                "temporary_access_link": f"/setup/{temp_token}",
                "temp_password": temp_password,  # In production, send via email
                "token_expiry": expiry_time.isoformat()
            }

        except Exception as e:
            db.rollback()
            logger.error(
                "Company bootstrap failed",
                error=str(e),
                company_name=company_name,
                superadmin_id=superadmin_user.id
            )
            raise ValueError(f"Company bootstrap failed: {str(e)}")

    @staticmethod
    def _generate_temp_password(length: int = 12) -> str:
        """Generate a secure temporary password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def _generate_temp_token() -> str:
        """Generate a secure temporary access token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_bootstrap_token(token: str) -> bool:
        """Validate temporary access token (placeholder for future implementation)"""
        # In production, store tokens in Redis with expiry
        return len(token) > 0

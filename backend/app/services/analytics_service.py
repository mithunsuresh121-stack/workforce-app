from datetime import datetime, timedelta

import structlog
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.channels import Channel, ChannelType
from app.models.company import Company
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam
from app.models.meetings import Meeting, MeetingStatus
from app.models.user import User, UserRole

logger = structlog.get_logger(__name__)


class AnalyticsService:
    @staticmethod
    def get_user_stats(db: Session, company_id: int = None) -> dict:
        """Get user statistics including counts by role, department, team, and active users"""
        query = db.query(User)

        if company_id:
            query = query.filter(User.company_id == company_id)

        # Total users
        total_users = query.count()

        # Users by role
        role_counts = (
            query.with_entities(User.role, func.count(User.id).label("count"))
            .group_by(User.role)
            .all()
        )
        by_role = {role.value: count for role, count in role_counts}

        # Users by department
        dept_counts = (
            query.join(CompanyDepartment, User.department_id == CompanyDepartment.id)
            .with_entities(CompanyDepartment.name, func.count(User.id).label("count"))
            .group_by(CompanyDepartment.name)
            .all()
        )
        by_department = {name: count for name, count in dept_counts}

        # Users by team
        team_counts = (
            query.join(CompanyTeam, User.team_id == CompanyTeam.id)
            .with_entities(CompanyTeam.name, func.count(User.id).label("count"))
            .group_by(CompanyTeam.name)
            .all()
        )
        by_team = {name: count for name, count in team_counts}

        # Active users (last active within 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = query.filter(
            User.is_active == True, User.last_active >= thirty_days_ago
        ).count()

        return {
            "total_users": total_users,
            "by_role": by_role,
            "by_department": by_department,
            "by_team": by_team,
            "active_users": active_users,
        }

    @staticmethod
    def get_channel_stats(db: Session, company_id: int = None) -> dict:
        """Get channel statistics including counts by type and activity metrics"""
        query = db.query(Channel)

        if company_id:
            query = query.filter(Channel.company_id == company_id)

        # Total channels
        total_channels = query.count()

        # Channels by type
        from sqlalchemy import func

        type_counts = (
            query.with_entities(Channel.type, func.count(Channel.id).label("count"))
            .group_by(Channel.type)
            .all()
        )
        by_type = {channel_type.value: count for channel_type, count in type_counts}

        # Active channels (with messages in last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_channels = query.filter(
            Channel.last_message_at >= seven_days_ago
        ).count()

        # Average members per channel (using ChannelMember)
        from sqlalchemy import func

        from app.models.channels import ChannelMember

        subq_members = (
            db.query(func.count(ChannelMember.user_id).label("member_count"))
            .join(Channel, ChannelMember.channel_id == Channel.id)
            .filter(Channel.company_id == company_id if company_id else True)
            .group_by(Channel.id)
            .subquery()
        )
        avg_members = db.query(func.avg(subq_members.c.member_count)).scalar() or 0

        return {
            "total_channels": total_channels,
            "by_type": by_type,
            "active_channels": active_channels,
            "average_members_per_channel": round(avg_members, 2),
        }

    @staticmethod
    def get_meeting_stats(db: Session, company_id: int = None) -> dict:
        """Get meeting statistics including counts by status and participation metrics"""
        query = db.query(Meeting)

        if company_id:
            query = query.filter(Meeting.company_id == company_id)

        # Total meetings
        total_meetings = query.count()

        # Meetings by status
        from sqlalchemy import func

        status_counts = (
            query.with_entities(Meeting.status, func.count(Meeting.id).label("count"))
            .group_by(Meeting.status)
            .all()
        )
        by_status = {status.value: count for status, count in status_counts}

        # Average participants per meeting
        from sqlalchemy import func

        from app.models.meeting_participants import MeetingParticipant

        subq_participants = (
            db.query(func.count(MeetingParticipant.user_id).label("participant_count"))
            .join(Meeting, MeetingParticipant.meeting_id == Meeting.id)
            .filter(Meeting.company_id == company_id if company_id else True)
            .group_by(Meeting.id)
            .subquery()
        )
        avg_participants = (
            db.query(func.avg(subq_participants.c.participant_count)).scalar() or 0
        )

        # Upcoming meetings (next 7 days)
        seven_days_from_now = datetime.utcnow() + timedelta(days=7)
        upcoming_meetings = query.filter(
            Meeting.start_time >= datetime.utcnow(),
            Meeting.start_time <= seven_days_from_now,
        ).count()

        return {
            "total_meetings": total_meetings,
            "by_status": by_status,
            "average_participants_per_meeting": round(avg_participants, 2),
            "upcoming_meetings": upcoming_meetings,
        }

    @staticmethod
    def get_audit_stats(db: Session, company_id: int = None) -> dict:
        """Get audit log summaries including counts by event type and recent activity"""
        query = db.query(AuditLog)

        if company_id:
            query = query.filter(AuditLog.company_id == company_id)

        # Total audit events
        total_events = query.count()

        # Events by type (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        type_counts = (
            query.filter(AuditLog.created_at >= thirty_days_ago)
            .with_entities(AuditLog.event_type, func.count(AuditLog.id).label("count"))
            .group_by(AuditLog.event_type)
            .all()
        )
        by_event_type = {event_type: count for event_type, count in type_counts}

        # Recent events (last 24 hours)
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        recent_events = query.filter(AuditLog.created_at >= one_day_ago).count()

        # Top users by audit activity (last 30 days)
        top_users = (
            query.filter(AuditLog.created_at >= thirty_days_ago)
            .with_entities(AuditLog.user_id, func.count(AuditLog.id).label("count"))
            .group_by(AuditLog.user_id)
            .order_by(func.count(AuditLog.id).desc())
            .limit(5)
            .all()
        )
        top_users_by_activity = [
            {"user_id": uid, "event_count": count} for uid, count in top_users
        ]

        return {
            "total_audit_events": total_events,
            "by_event_type_last_30_days": by_event_type,
            "recent_events_last_24_hours": recent_events,
            "top_users_by_activity": top_users_by_activity,
        }

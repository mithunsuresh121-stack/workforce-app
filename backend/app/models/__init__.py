# Import all models to ensure they are registered with SQLAlchemy
from .company import Company
from .company_department import CompanyDepartment
from .company_team import CompanyTeam
from .user import User
from .task import Task
from .leave import Leave
from .shift import Shift
from .swap_request import SwapRequest
from .employee_profile import EmployeeProfile
from .profile_update_request import ProfileUpdateRequest
from .attendance import Attendance, Break
from .notification import Notification
from .notification_preferences import NotificationPreferences
from .notification_digest import NotificationDigest
from .payroll import (
    Employee,
    Salary,
    Allowance,
    Deduction,
    Bonus,
    PayrollRun,
    PayrollEntry
)
from .refresh_token import RefreshToken
from .chat import ChatMessage
from .announcement import Announcement
from .document import Document
from .attachment import Attachment
from .channels import Channel, ChannelMember
from .message_reactions import MessageReaction
from .meetings import Meeting
from .meeting_participants import MeetingParticipant

__all__ = [
    "Company",
    "CompanyDepartment",
    "CompanyTeam",
    "User",
    "Task",
    "Leave",
    "Shift",
    "SwapRequest",
    "EmployeeProfile",
    "ProfileUpdateRequest",
    "Attendance",
    "Break",
    "Notification",
    "NotificationPreferences",
    "NotificationDigest",
    "Employee",
    "Salary",
    "Allowance",
    "Deduction",
    "Bonus",
    "PayrollRun",
    "PayrollEntry",
    "RefreshToken",
    "ChatMessage",
    "Announcement",
    "Document",
    "Attachment",
    "Channel",
    "ChannelMember",
    "MessageReaction",
    "Meeting",
    "MeetingParticipant"
]

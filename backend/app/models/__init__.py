# Import all models to ensure they are registered with SQLAlchemy
from app.company import Company
from app.user import User
from app.task import Task
from app.leave import Leave
from app.shift import Shift
from app.swap_request import SwapRequest
from app.employee_profile import EmployeeProfile
from app.profile_update_request import ProfileUpdateRequest
from app.attendance import Attendance, Break
from app.notification import Notification
from app.notification_preferences import NotificationPreferences
from app.notification_digest import NotificationDigest
from app.payroll import (
    Employee,
    Salary,
    Allowance,
    Deduction,
    Bonus,
    PayrollRun,
    PayrollEntry
)
from app.refresh_token import RefreshToken
from app.chat import ChatMessage
from app.announcement import Announcement
from app.document import Document
from app.attachment import Attachment

__all__ = [
    "Company",
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
    "Attachment"
]

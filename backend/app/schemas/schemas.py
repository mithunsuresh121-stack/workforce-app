from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class Role(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    DEPARTMENT_ADMIN = "DEPARTMENT_ADMIN"
    TEAM_LEAD = "TEAM_LEAD"
    EMPLOYEE = "EMPLOYEE"


class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"

    @classmethod
    def _missing_(cls, value):
        # Handle case-insensitive matching
        for member in cls:
            if member.value.lower() == str(value).lower():
                return member
        return super()._missing_(value)


class LeaveStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CompanyOut(BaseModel):
    id: int
    name: str
    domain: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    invite_token: Optional[str] = None  # For invite-based signup


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[Role] = None
    company_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: Role
    company_id: Optional[int] = None  # None for Super Admin users
    company: Optional[CompanyOut] = None  # Include company details
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: str = "Pending"  # Changed to string to avoid enum serialization issues
    priority: Optional[str] = "Medium"
    assignee_id: Optional[int] = None
    assigned_by: Optional[int] = None
    due_at: Optional[datetime] = None

    @validator("status", pre=True, always=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            # Handle case-insensitive matching
            status_map = {
                "pending": "Pending",
                "in progress": "In Progress",
                "completed": "Completed",
                "overdue": "Overdue",
                "PENDING": "Pending",
                "IN_PROGRESS": "In Progress",
                "COMPLETED": "Completed",
                "OVERDUE": "Overdue",
            }
            return status_map.get(v.lower().replace("_", " "), v)
        elif hasattr(v, "value"):
            return v.value
        return v


class TaskCreate(TaskBase):
    company_id: int


class TaskOut(TaskBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    attachments: List["AttachmentOut"] = []

    class Config:
        from_attributes = True


# Attachment Schemas
class AttachmentBase(BaseModel):
    file_path: str
    file_type: str
    file_size: float
    uploaded_at: datetime


class AttachmentCreate(BaseModel):
    pass  # File upload handled separately


class AttachmentOut(AttachmentBase):
    id: int
    task_id: int
    uploaded_by: int

    class Config:
        from_attributes = True


# Notification Schemas
from enum import Enum


class NotificationType(str, Enum):
    TASK_ASSIGNED = "TASK_ASSIGNED"
    SHIFT_SCHEDULED = "SHIFT_SCHEDULED"
    SYSTEM_MESSAGE = "SYSTEM_MESSAGE"
    ADMIN_MESSAGE = "ADMIN_MESSAGE"


class NotificationStatus(str, Enum):
    UNREAD = "UNREAD"
    READ = "READ"


class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType
    status: NotificationStatus = NotificationStatus.UNREAD


class NotificationCreate(NotificationBase):
    user_id: int
    company_id: int


class NotificationOut(NotificationBase):
    id: int
    user_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# New Schemas for Leaves
class LeaveBase(BaseModel):
    tenant_id: str
    employee_id: int
    type: str
    start_at: datetime
    end_at: datetime
    status: LeaveStatus = LeaveStatus.PENDING

    @validator("type")
    def validate_leave_type(cls, v):
        valid_types = [
            "Vacation",
            "Sick Leave",
            "Personal Leave",
            "Maternity Leave",
            "Paternity Leave",
            "Bereavement Leave",
        ]
        if v not in valid_types:
            raise ValueError(
                f'Invalid leave type. Must be one of: {", ".join(valid_types)}'
            )
        return v

    @validator("end_at")
    def validate_end_at_after_start_at(cls, v, values):
        if "start_at" in values and v <= values["start_at"]:
            raise ValueError("end_at must be after start_at")
        return v


class LeaveCreate(LeaveBase):
    pass


class LeaveOut(BaseModel):
    id: int
    tenant_id: str
    employee_id: int
    type: str
    start_at: datetime
    end_at: datetime
    status: LeaveStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# New Schemas for Shifts
class ShiftBase(BaseModel):
    company_id: int
    employee_id: int
    start_at: datetime
    end_at: datetime
    location: Optional[str] = None


class ShiftCreate(ShiftBase):
    pass


class ShiftOut(ShiftBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# New Schemas for EmployeeProfile
class EmployeeProfileBase(BaseModel):
    user_id: int
    company_id: int
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    hire_date: Optional[datetime] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = True
    # gender: Optional[str] = None  # removed as per request
    address: Optional[str] = None
    city: Optional[str] = None
    emergency_contact: Optional[str] = None
    employee_id: Optional[str] = None
    profile_picture_url: Optional[str] = None


class EmployeeProfileCreate(EmployeeProfileBase):
    pass


class EmployeeProfileUpdate(BaseModel):
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    hire_date: Optional[datetime] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None
    # gender: Optional[str] = None  # removed as per request
    address: Optional[str] = None
    city: Optional[str] = None
    emergency_contact: Optional[str] = None
    employee_id: Optional[str] = None
    profile_picture_url: Optional[str] = None


class EmployeeProfileOut(EmployeeProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Payroll Status Enums
class PayrollStatus(str, Enum):
    DRAFT = "Draft"
    PROCESSED = "Processed"
    APPROVED = "Approved"
    PAID = "Paid"


class PayrollEntryStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"


# Payroll Schemas
class EmployeeBase(BaseModel):
    tenant_id: str
    user_id: int
    employee_id: str
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[datetime] = None
    base_salary: float
    status: str = "Active"


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalaryBase(BaseModel):
    tenant_id: str
    employee_id: int
    amount: float
    effective_date: datetime
    end_date: Optional[datetime] = None


class SalaryCreate(SalaryBase):
    pass


class SalaryOut(SalaryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AllowanceBase(BaseModel):
    tenant_id: str
    employee_id: int
    name: str
    amount: float
    type: str
    is_taxable: str = "Yes"
    effective_date: datetime
    end_date: Optional[datetime] = None


class AllowanceCreate(AllowanceBase):
    pass


class AllowanceOut(AllowanceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeductionBase(BaseModel):
    tenant_id: str
    employee_id: int
    name: str
    amount: float
    type: str
    is_mandatory: str = "Yes"
    effective_date: datetime
    end_date: Optional[datetime] = None


class DeductionCreate(DeductionBase):
    pass


class DeductionOut(DeductionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BonusBase(BaseModel):
    tenant_id: str
    employee_id: int
    name: str
    amount: float
    type: str
    payment_date: datetime
    status: str = "Pending"


class BonusCreate(BonusBase):
    pass


class BonusOut(BonusBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PayrollRunBase(BaseModel):
    tenant_id: str
    period_start: datetime
    period_end: datetime
    status: PayrollStatus = PayrollStatus.DRAFT
    total_gross: float = 0.0
    total_deductions: float = 0.0
    total_net: float = 0.0
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None


class PayrollRunCreate(PayrollRunBase):
    pass


class PayrollRunOut(PayrollRunBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PayrollEntryBase(BaseModel):
    payroll_run_id: int
    employee_id: int
    base_salary: float = 0.0
    total_allowances: float = 0.0
    total_deductions: float = 0.0
    total_bonuses: float = 0.0
    gross_pay: float = 0.0
    net_pay: float = 0.0
    status: PayrollEntryStatus = PayrollEntryStatus.PENDING
    notes: Optional[str] = None


class PayrollEntryCreate(PayrollEntryBase):
    pass


class PayrollEntryOut(PayrollEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Profile Update Request Schemas
class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ProfileUpdateRequestBase(BaseModel):
    user_id: int
    request_type: str  # "update" or "delete"
    payload: Optional[dict] = None


class ProfileUpdateRequestCreate(ProfileUpdateRequestBase):
    pass


class ProfileUpdateRequestOut(BaseModel):
    id: int
    user_id: int
    requested_by_id: int
    request_type: str
    payload: Optional[dict]
    status: RequestStatus
    created_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by_id: Optional[int]
    review_comment: Optional[str]

    class Config:
        from_attributes = True


class ProfileUpdateRequestReview(BaseModel):
    status: RequestStatus
    review_comment: Optional[str] = None


# Document Schemas
class DocumentType(str, Enum):
    POLICY = "POLICY"
    PAYSLIP = "PAYSLIP"
    NOTICE = "NOTICE"
    OTHER = "OTHER"


class DocumentBase(BaseModel):
    file_path: str
    type: DocumentType
    access_role: str  # "EMPLOYEE", "MANAGER", "ADMIN"


class DocumentCreate(DocumentBase):
    pass


class DocumentOut(DocumentBase):
    id: int
    company_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Announcement Schemas
class AnnouncementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementOut(AnnouncementBase):
    id: int
    company_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessageBase(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatMessageCreate(ChatMessageBase):
    receiver_id: Optional[int] = None  # None for company-wide


class ChatMessageResponse(ChatMessageBase):
    id: int
    company_id: int
    sender_id: int
    receiver_id: Optional[int]
    channel_id: Optional[int]
    attachments: List[Dict[str, Any]] = []
    is_read: bool
    edited_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageUpdate(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


# Channel Schemas
class ChannelType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"
    PUBLIC = "public"


class ChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: ChannelType


class ChannelCreate(ChannelBase):
    pass


class ChannelResponse(ChannelBase):
    id: int
    company_id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# Reaction Schemas
class ReactionCreate(BaseModel):
    emoji: str = Field(..., min_length=1, max_length=10)


# Meeting Schemas
class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class ParticipantRole(str, Enum):
    ORGANIZER = "organizer"
    PARTICIPANT = "participant"


class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
    participant_ids: List[int] = []


class MeetingCreate(MeetingBase):
    pass


class MeetingResponse(MeetingBase):
    id: int
    organizer_id: int
    company_id: int
    status: MeetingStatus
    link: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingParticipantResponse(BaseModel):
    id: int
    meeting_id: int
    user_id: int
    role: ParticipantRole
    join_time: Optional[datetime]
    leave_time: Optional[datetime]

    class Config:
        from_attributes = True


# WebSocket Notification Schema
class WebSocketNotification(BaseModel):
    type: str  # e.g., "new_message", "announcement", "system_alert"
    data: dict  # Flexible data payload
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Reports Schemas
from typing import Any, Dict


class AttendanceHeatmap(BaseModel):
    date: str  # YYYY-MM-DD
    present: int
    absent: int
    heatmap_intensity: int  # 0-100 based on attendance rate


class PayrollProjection(BaseModel):
    dept: str
    projected_cost: float
    employees: int
    forecast_next_month: float


class OvertimeTrend(BaseModel):
    period: str  # e.g., "2024-W01" or "2024-01"
    dept: str
    hours: float


class ReportExportResponse(BaseModel):
    file_url: Optional[str] = None  # For download URL
    content: Optional[bytes] = None  # For blob download
    filename: str
    content_type: str  # "text/csv" or "application/pdf"

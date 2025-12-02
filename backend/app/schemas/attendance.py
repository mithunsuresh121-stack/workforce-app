from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BreakBase(BaseModel):
    break_type: str = "lunch"
    notes: Optional[str] = None


class BreakCreate(BreakBase):
    attendance_id: int
    break_start: datetime


class BreakUpdate(BaseModel):
    break_end: Optional[datetime] = None
    break_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class Break(BreakBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attendance_id: int
    break_start: datetime
    break_end: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    created_at: datetime


class AttendanceBase(BaseModel):
    employee_id: int
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    clock_in_time: datetime


class AttendanceUpdate(BaseModel):
    clock_out_time: Optional[datetime] = None
    total_hours: Optional[float] = None
    overtime_hours: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Attendance(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clock_in_time: datetime
    clock_out_time: Optional[datetime] = None
    total_hours: Optional[float] = None
    overtime_hours: float = 0.0
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None
    breaks: List[Break] = []


class AttendanceSummary(BaseModel):
    total_days: int
    total_hours: float
    overtime_hours: float
    average_hours_per_day: float
    attendance_records: List[Attendance]


class ClockInRequest(BaseModel):
    employee_id: int
    notes: Optional[str] = None


class ClockOutRequest(BaseModel):
    employee_id: int
    attendance_id: int
    notes: Optional[str] = None


class BreakStartRequest(BaseModel):
    break_type: str = "lunch"
    attendance_id: Optional[int] = None
    notes: Optional[str] = None


class BreakEndRequest(BaseModel):
    notes: Optional[str] = None

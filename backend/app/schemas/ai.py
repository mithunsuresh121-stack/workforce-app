from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class AICapability(str, Enum):
    READ_TEAM_DATA = "READ_TEAM_DATA"
    READ_COMPANY_DATA = "READ_COMPANY_DATA"
    GENERATE_SUMMARY = "GENERATE_SUMMARY"
    SUGGEST_TASKS = "SUGGEST_TASKS"

class AIDecision(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"

class AIQueryRequest(BaseModel):
    query_text: str
    capability: AICapability
    scope_company_id: Optional[int] = None
    scope_department_id: Optional[int] = None
    scope_team_id: Optional[int] = None

class AIQueryResponse(BaseModel):
    status: AIDecision
    reason: str
    mock_response: str
    approval_required: bool = False

class AIPolicyUpdate(BaseModel):
    capability: AICapability
    required_role: str  # UserRole enum value
    approval_required: bool = False

class AIApprovalRequest(BaseModel):
    ai_request_id: int
    approved: bool
    approver_notes: Optional[str] = None

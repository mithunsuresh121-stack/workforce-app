from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class AICapability(str, Enum):
    READ_TEAM_DATA = "READ_TEAM_DATA"
    READ_COMPANY_DATA = "READ_COMPANY_DATA"
    GENERATE_SUMMARY = "GENERATE_SUMMARY"
    SUGGEST_TASKS = "SUGGEST_TASKS"

class AIDecision(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"

class AIPolicyType(str, Enum):
    SCOPE_RBAC = "SCOPE_RBAC"
    PROHIBITED_CONTENT = "PROHIBITED_CONTENT"
    SENTIMENT_TOXICITY = "SENTIMENT_TOXICITY"
    JAILBREAK_DETECTION = "JAILBREAK_DETECTION"

class AIPolicySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

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

class AIPolicyViolation(BaseModel):
    policy_type: AIPolicyType
    severity: AIPolicySeverity
    details: Dict[str, str]
    confidence_score: Optional[float] = None

class TrustScoreUpdate(BaseModel):
    user_id: int
    new_score: int
    reason: str
    violation_type: Optional[AIPolicyType] = None

class RiskAssessment(BaseModel):
    user_id: int
    capability: str
    risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: Dict[str, float]
    context: Dict[str, Any]
    timestamp: datetime

class PolicyRule(BaseModel):
    rule_id: str
    conditions: Dict[str, Any]
    actions: List[str]
    priority: int = 100

class PolicyDSL(BaseModel):
    rules: List[PolicyRule]
    version: str = "1.0"

class ApprovalRequest(BaseModel):
    request_type: str
    request_data: Dict[str, Any]
    risk_score: Optional[int] = None
    priority: str = "medium"  # low, medium, high, critical
    notes: Optional[str] = None

class ApprovalDecision(BaseModel):
    approval_id: int
    decision: str  # approved, rejected, escalated
    notes: Optional[str] = None

class AutoRestriction(BaseModel):
    user_id: int
    level: str  # none, cooldown, limited, blocked
    reason: str
    expires_at: datetime
    risk_level: str

class RiskHeatMapData(BaseModel):
    company_id: Optional[int] = None
    time_range_hours: int = 24
    risk_levels: Dict[str, int]  # LOW, MEDIUM, HIGH, CRITICAL -> count

class ComplianceExportRequest(BaseModel):
    company_id: Optional[int] = None
    start_date: str
    end_date: str
    include_policies: bool = True
    include_logs: bool = True
    include_trust_history: bool = True
    format: str = "pdf"  # pdf or json

class WebhookAlertConfig(BaseModel):
    url: str
    headers: Optional[Dict[str, str]] = None
    enabled: bool = True
    alert_types: List[str] = ["HIGH", "CRITICAL"]  # severity levels to alert on

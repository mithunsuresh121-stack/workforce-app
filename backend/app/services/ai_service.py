import structlog
from sqlalchemy.orm import Session
from app.schemas.ai import AICapability, AIDecision, AIQueryRequest, AIQueryResponse
from app.models.user import User, UserRole
from app.core.rbac import RBACService
from app.services.audit_service import AuditService
from app.services.security_service import SecurityService, SecurityEvent, SecuritySeverity

logger = structlog.get_logger(__name__)

class AIService:
    @staticmethod
    def process_ai_query(db: Session, user: User, request: AIQueryRequest) -> AIQueryResponse:
        """Process AI query with security checks and logging"""

        # Step 1: Validate scope isolation
        scope_valid = AIService._validate_scope(user, request)
        if not scope_valid:
            # Log cross-org violation
            AuditService.log_ai_event(
                db=db,
                user_id=user.id,
                company_id=user.company_id,
                request_text=request.query_text,
                capability=request.capability.value,
                decision="blocked",
                scope_valid=False,
                required_role=user.role.value,
                user_role=user.role.value,
                severity="high"
            )

            # Security event for cross-org
            SecurityService.log_security_event(
                db=db,
                event_type=SecurityEvent.AI_CROSS_ORG,
                user_id=user.id,
                company_id=user.company_id,
                severity=SecuritySeverity.MEDIUM,
                details={
                    "capability": request.capability.value,
                    "scope_company_id": request.scope_company_id,
                    "scope_department_id": request.scope_department_id,
                    "scope_team_id": request.scope_team_id
                }
            )

            return AIQueryResponse(
                status=AIDecision.BLOCKED,
                reason="Cross-organization access not allowed",
                mock_response="Access denied"
            )

        # Step 2: Check RBAC permissions
        allowed, required_role = RBACService.can_use_ai_capability(
            user=user,
            capability=request.capability.value,
            scope_company_id=request.scope_company_id,
            scope_department_id=request.scope_department_id,
            scope_team_id=request.scope_team_id
        )

        if not allowed:
            # Log unauthorized capability
            AuditService.log_ai_event(
                db=db,
                user_id=user.id,
                company_id=user.company_id,
                request_text=request.query_text,
                capability=request.capability.value,
                decision="blocked",
                scope_valid=True,
                required_role=required_role,
                user_role=user.role.value,
                severity="high"
            )

            # Security event for unauthorized capability
            SecurityService.log_security_event(
                db=db,
                event_type=SecurityEvent.AI_UNAUTHORIZED_CAPABILITY,
                user_id=user.id,
                company_id=user.company_id,
                severity=SecuritySeverity.MEDIUM,
                details={
                    "capability": request.capability.value,
                    "required_role": required_role,
                    "user_role": user.role.value
                }
            )

            return AIQueryResponse(
                status=AIDecision.BLOCKED,
                reason=f"Insufficient permissions. Required role: {required_role}",
                mock_response="Access denied"
            )

        # Step 3: Check for approval requirements (SUPERADMIN dangerous actions)
        if user.role == UserRole.SUPERADMIN and AIService._requires_approval(request.capability):
            # For now, block without approval workflow (can be extended)
            AuditService.log_ai_event(
                db=db,
                user_id=user.id,
                company_id=user.company_id,
                request_text=request.query_text,
                capability=request.capability.value,
                decision="pending_approval",
                scope_valid=True,
                required_role=user.role.value,
                user_role=user.role.value,
                severity="low"
            )

            SecurityService.log_security_event(
                db=db,
                event_type=SecurityEvent.AI_ADMIN_NO_SIGNOFF,
                user_id=user.id,
                company_id=user.company_id,
                severity=SecuritySeverity.LOW,
                details={"capability": request.capability.value}
            )

            return AIQueryResponse(
                status=AIDecision.PENDING_APPROVAL,
                reason="Superadmin action requires human approval",
                mock_response="Pending approval",
                approval_required=True
            )

        # Step 4: Allow and log
        AuditService.log_ai_event(
            db=db,
            user_id=user.id,
            company_id=user.company_id,
            request_text=request.query_text,
            capability=request.capability.value,
            decision="allowed",
            scope_valid=True,
            required_role=user.role.value,
            user_role=user.role.value,
            severity="low"
        )

        # Mock AI response
        mock_response = AIService._generate_mock_response(request.capability)

        return AIQueryResponse(
            status=AIDecision.ALLOWED,
            reason="Query processed successfully",
            mock_response=mock_response
        )

    @staticmethod
    def _validate_scope(user: User, request: AIQueryRequest) -> bool:
        """Validate that the requested scope matches user's org boundaries"""
        if request.scope_company_id and user.company_id != request.scope_company_id:
            return False
        if request.scope_department_id and user.department_id != request.scope_department_id:
            return False
        if request.scope_team_id and user.team_id != request.scope_team_id:
            return False
        return True

    @staticmethod
    def _requires_approval(capability: AICapability) -> bool:
        """Check if capability requires approval for SUPERADMIN"""
        # For now, all SUPERADMIN actions require approval (can be configured)
        return True

    @staticmethod
    def _generate_mock_response(capability: AICapability) -> str:
        """Generate mock AI response based on capability"""
        responses = {
            AICapability.READ_TEAM_DATA: "Mock response: Team data retrieved successfully",
            AICapability.READ_COMPANY_DATA: "Mock response: Company data retrieved successfully",
            AICapability.GENERATE_SUMMARY: "Mock response: Summary generated",
            AICapability.SUGGEST_TASKS: "Mock response: Task suggestions provided"
        }
        return responses.get(capability, "Mock AI response")

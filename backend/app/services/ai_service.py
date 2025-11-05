import structlog
import re
import requests
from sqlalchemy.orm import Session
from app.schemas.ai import (
    AICapability, AIDecision, AIQueryRequest, AIQueryResponse,
    AIPolicyType, AIPolicySeverity, AIPolicyViolation
)
from app.models.user import User, UserRole
from app.core.rbac import RBACService
from app.services.audit_service import AuditService
from app.services.security_service import SecurityService, SecurityEvent, SecuritySeverity
from app.services.trust_service import TrustService

logger = structlog.get_logger(__name__)

class AIService:
    # Prohibited content patterns
    PROHIBITED_PATTERNS = [
        r'\b(hack|exploit|breach|attack)\b',
        r'\b(password|credential|secret)\b.*\b(steal|leak|expose)\b',
        r'\b(malware|virus|ransomware)\b',
        r'\b(illegal|unlawful|criminal)\b.*\b(activity|action)\b'
    ]

    # Jailbreak detection patterns
    JAILBREAK_PATTERNS = [
        r'ignore.*instruction',
        r'act as.*admin',
        r'administrator',
        r'\b(developer mode|debug mode|god mode)\b',
        r'\b(DAN|uncensored|unrestricted)\b'
    ]

    @staticmethod
    def process_ai_query(db: Session, user: User, request: AIQueryRequest) -> AIQueryResponse:
        """Process AI query with comprehensive security checks and logging"""

        # Step 0: Check trust score and access limits
        trust_score = TrustService.get_trust_score(db, user.id)
        access_limits = TrustService.get_access_limits(trust_score)

        if request.capability.value not in access_limits["allowed_capabilities"] and "all" not in access_limits["allowed_capabilities"]:
            return AIQueryResponse(
                status=AIDecision.BLOCKED,
                reason=f"Access denied due to low trust score. Current tier: {TrustService.get_trust_tier(trust_score)}",
                mock_response="Access denied"
            )

        # Step 1: Pre-execution content policy checks
        content_violations = AIService._check_content_policies(request.query_text)
        if content_violations:
            # Apply trust score decay
            for violation in content_violations:
                TrustService.update_trust_score(
                    db, user.id, violation.policy_type, violation.severity,
                    f"Content policy violation: {violation.policy_type.value}"
                )

            # Log violation
            AuditService.log_ai_event(
                db=db,
                user_id=user.id,
                company_id=user.company_id,
                request_text=request.query_text,
                capability=request.capability.value,
                decision="blocked",
                scope_valid=True,
                required_role=user.role.value,
                user_role=user.role.value,
                severity=content_violations[0].severity.value.lower(),
                details={"violations": [v.model_dump() for v in content_violations]}
            )

            return AIQueryResponse(
                status=AIDecision.BLOCKED,
                reason=f"Content policy violation detected: {content_violations[0].policy_type.value}",
                mock_response="Access denied"
            )

        # Step 2: Validate scope isolation
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

        # Step 4: Post-execution response validation (placeholder for future AI response analysis)
        # This would analyze the actual AI response for policy violations

        # Step 5: Allow and log
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

        # Update trust score positively for clean usage
        TrustService.update_trust_score(db, user.id, reason="Clean AI usage")

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
    def _check_content_policies(text: str) -> list[AIPolicyViolation]:
        """Check text against content policies and return violations"""
        violations = []

        # Check prohibited content
        for pattern in AIService.PROHIBITED_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(AIPolicyViolation(
                    policy_type=AIPolicyType.PROHIBITED_CONTENT,
                    severity=AIPolicySeverity.HIGH,
                    details={"pattern": pattern, "matched_text": text},
                    confidence_score=0.9
                ))

        # Check jailbreak attempts
        for pattern in AIService.JAILBREAK_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(AIPolicyViolation(
                    policy_type=AIPolicyType.JAILBREAK_DETECTION,
                    severity=AIPolicySeverity.CRITICAL,
                    details={"pattern": pattern, "matched_text": text},
                    confidence_score=0.95
                ))

        # Sentiment/toxicity check (placeholder - would integrate with external API)
        toxicity_score = AIService._check_toxicity(text)
        if toxicity_score > 0.7:
            violations.append(AIPolicyViolation(
                policy_type=AIPolicyType.SENTIMENT_TOXICITY,
                severity=AIPolicySeverity.MEDIUM if toxicity_score < 0.9 else AIPolicySeverity.HIGH,
                details={"toxicity_score": str(toxicity_score)},
                confidence_score=toxicity_score
            ))

        return violations

    @staticmethod
    def _check_toxicity(text: str) -> float:
        """Placeholder for toxicity detection - returns mock score"""
        # In production, this would call an external toxicity detection API
        toxic_words = ['hate', 'stupid', 'idiot', 'dumb', 'terrible']
        found_toxic = sum(1 for word in toxic_words if word in text.lower())
        score = found_toxic / len(toxic_words) if found_toxic > 0 else 0.0
        return min(score, 1.0)

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

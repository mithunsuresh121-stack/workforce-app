import json
from datetime import datetime, timedelta
from io import BytesIO

import structlog
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.ai import ComplianceExportRequest
from app.services.trust_service import TrustService

logger = structlog.get_logger(__name__)


class ComplianceExportService:
    @staticmethod
    def generate_compliance_report(
        db: Session, request: ComplianceExportRequest
    ) -> dict:
        """Generate comprehensive compliance report"""
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)

        report_data = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "date_range": {"start": request.start_date, "end": request.end_date},
                "company_id": request.company_id,
                "format": request.format,
            },
            "policies_in_effect": ComplianceExportService._get_policies_in_effect(),
            "violation_summary": {},
            "trust_score_history": {},
            "detailed_logs": [],
        }

        if request.include_logs:
            report_data["detailed_logs"] = ComplianceExportService._get_detailed_logs(
                db, request.company_id, start_date, end_date
            )

        if request.include_trust_history:
            report_data["trust_score_history"] = (
                ComplianceExportService._get_trust_history(
                    db, request.company_id, start_date, end_date
                )
            )

        # Generate summary statistics
        report_data["violation_summary"] = (
            ComplianceExportService._calculate_violation_summary(
                report_data["detailed_logs"]
            )
        )

        return report_data

    @staticmethod
    def _get_policies_in_effect() -> dict:
        """Get current policies configuration"""
        from app.services.ai_service import AIService

        return {
            "content_policies": {
                "prohibited_patterns": AIService.PROHIBITED_PATTERNS,
                "jailbreak_patterns": AIService.JAILBREAK_PATTERNS,
                "toxicity_threshold": 0.7,
            },
            "trust_scoring": {
                "max_score": TrustService.MAX_TRUST_SCORE,
                "decay_rates": {
                    "LOW": TrustService.DECAY_RATE_LOW,
                    "MEDIUM": TrustService.DECAY_RATE_MEDIUM,
                    "HIGH": TrustService.DECAY_RATE_HIGH,
                    "CRITICAL": TrustService.DECAY_RATE_CRITICAL,
                },
                "recovery_rate": TrustService.RECOVERY_RATE,
                "recovery_threshold_days": TrustService.RECOVERY_THRESHOLD_DAYS,
            },
            "access_tiers": {
                "PLATINUM": TrustService.get_access_limits(95),
                "GOLD": TrustService.get_access_limits(85),
                "SILVER": TrustService.get_access_limits(60),
                "BRONZE": TrustService.get_access_limits(30),
                "RESTRICTED": TrustService.get_access_limits(10),
            },
        }

    @staticmethod
    def _get_detailed_logs(
        db: Session, company_id: int, start_date: datetime, end_date: datetime
    ) -> list:
        """Get detailed audit logs for the period"""
        query = (
            db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.created_at >= start_date,
                    AuditLog.created_at <= end_date,
                    or_(
                        AuditLog.event_type.like("AI_%"),
                        AuditLog.event_type.like("SECURITY_AI_%"),
                        AuditLog.event_type == "TRUST_SCORE_UPDATE",
                    ),
                )
            )
            .order_by(AuditLog.created_at)
        )

        if company_id:
            query = query.filter(AuditLog.company_id == company_id)

        logs = query.all()

        return [
            {
                "id": log.id,
                "event_type": log.event_type,
                "user_id": log.user_id,
                "company_id": log.company_id,
                "timestamp": log.created_at.isoformat(),
                "details": log.details,
                "ai_request_text": log.ai_request_text,
                "ai_capability": log.ai_capability,
                "ai_decision": log.ai_decision,
                "ai_scope_valid": log.ai_scope_valid,
                "ai_required_role": log.ai_required_role,
                "ai_user_role": log.ai_user_role,
                "ai_severity": log.ai_severity,
                "user_email": log.user.email if log.user else None,
            }
            for log in logs
        ]

    @staticmethod
    def _get_trust_history(
        db: Session, company_id: int, start_date: datetime, end_date: datetime
    ) -> dict:
        """Get trust score history for all users in the period"""
        trust_logs = db.query(AuditLog).filter(
            and_(
                AuditLog.event_type == "TRUST_SCORE_UPDATE",
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date,
            )
        )

        if company_id:
            trust_logs = trust_logs.filter(AuditLog.company_id == company_id)

        trust_logs = trust_logs.order_by(AuditLog.created_at).all()

        history = {}
        for log in trust_logs:
            user_id = log.user_id
            if user_id not in history:
                history[user_id] = []

            history[user_id].append(
                {
                    "timestamp": log.created_at.isoformat(),
                    "old_score": log.details.get("old_score"),
                    "new_score": log.details.get("new_score"),
                    "reason": log.details.get("reason"),
                    "violation_type": log.details.get("violation_type"),
                    "severity": log.details.get("severity"),
                }
            )

        return history

    @staticmethod
    def _calculate_violation_summary(logs: list) -> dict:
        """Calculate violation statistics from logs"""
        summary = {
            "total_events": len(logs),
            "violations_by_type": {},
            "violations_by_severity": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "violations_by_user": {},
            "ai_decisions": {"allowed": 0, "blocked": 0, "pending_approval": 0},
        }

        for log in logs:
            event_type = log["event_type"]

            # Count by event type
            if event_type not in summary["violations_by_type"]:
                summary["violations_by_type"][event_type] = 0
            summary["violations_by_type"][event_type] += 1

            # Count AI decisions
            if log.get("ai_decision"):
                decision = log["ai_decision"]
                if decision in summary["ai_decisions"]:
                    summary["ai_decisions"][decision] += 1

            # Count by severity
            severity = log.get("ai_severity", "LOW")
            if severity and severity.upper() in summary["violations_by_severity"]:
                summary["violations_by_severity"][severity.upper()] += 1

            # Count by user
            user_id = log["user_id"]
            if user_id not in summary["violations_by_user"]:
                summary["violations_by_user"][user_id] = {
                    "count": 0,
                    "email": log.get("user_email"),
                }
            summary["violations_by_user"][user_id]["count"] += 1

        return summary

    @staticmethod
    def generate_pdf_report(report_data: dict) -> BytesIO:
        """Generate PDF version of compliance report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            spaceAfter=30,
        )
        story.append(Paragraph("AI Governance Compliance Report", title_style))
        story.append(Spacer(1, 12))

        # Metadata
        meta = report_data["report_metadata"]
        story.append(Paragraph(f"Generated: {meta['generated_at']}", styles["Normal"]))
        story.append(
            Paragraph(
                f"Period: {meta['date_range']['start']} to {meta['date_range']['end']}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 20))

        # Violation Summary
        story.append(Paragraph("Violation Summary", styles["Heading2"]))
        summary = report_data["violation_summary"]

        summary_data = [
            ["Metric", "Value"],
            ["Total Events", str(summary["total_events"])],
            ["Allowed AI Requests", str(summary["ai_decisions"]["allowed"])],
            ["Blocked AI Requests", str(summary["ai_decisions"]["blocked"])],
            ["Pending Approvals", str(summary["ai_decisions"]["pending_approval"])],
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Severity breakdown
        story.append(Paragraph("Violations by Severity", styles["Heading3"]))
        severity_data = [["Severity", "Count"]]
        for severity, count in summary["violations_by_severity"].items():
            severity_data.append([severity, str(count)])

        severity_table = Table(severity_data)
        severity_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(severity_table)

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def export_report(db: Session, request: ComplianceExportRequest) -> dict:
        """Main export function - returns report in requested format"""
        report_data = ComplianceExportService.generate_compliance_report(db, request)

        if request.format.lower() == "pdf":
            pdf_buffer = ComplianceExportService.generate_pdf_report(report_data)
            return {
                "format": "pdf",
                "data": pdf_buffer.getvalue(),
                "filename": f"ai_compliance_report_{request.start_date}_to_{request.end_date}.pdf",
            }
        else:  # JSON format
            return {
                "format": "json",
                "data": json.dumps(report_data, indent=2),
                "filename": f"ai_compliance_report_{request.start_date}_to_{request.end_date}.json",
            }

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import structlog
from sqlalchemy.orm import Session

from app.schemas.ai import AIPolicySeverity, AIPolicyType
from app.services.audit_chain_service import AuditChainService
from app.services.audit_service import AuditService

logger = structlog.get_logger(__name__)


class PolicyRule:
    """Represents a single policy rule with conditions and actions"""

    def __init__(
        self,
        rule_id: str,
        conditions: Dict[str, Any],
        actions: List[str],
        priority: int = 100,
    ):
        self.rule_id = rule_id
        self.conditions = conditions
        self.actions = actions
        self.priority = priority

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if this rule's conditions match the context"""
        for condition_key, condition_value in self.conditions.items():
            if condition_key not in context:
                return False

            context_value = context[condition_key]

            # Handle different condition types
            if isinstance(condition_value, dict):
                if not self._evaluate_condition(context_value, condition_value):
                    return False
            else:
                # Simple equality check
                if context_value != condition_value:
                    return False

        return True

    def _evaluate_condition(
        self, context_value: Any, condition: Dict[str, Any]
    ) -> bool:
        """Evaluate a complex condition (gt, lt, in, regex, etc.)"""
        operator = condition.get("op", "eq")

        if operator == "gt":
            return context_value > condition["value"]
        elif operator == "gte":
            return context_value >= condition["value"]
        elif operator == "lt":
            return context_value < condition["value"]
        elif operator == "lte":
            return context_value <= condition["value"]
        elif operator == "in":
            return context_value in condition["value"]
        elif operator == "nin":
            return context_value not in condition["value"]
        elif operator == "regex":
            return bool(re.search(condition["pattern"], str(context_value)))
        elif operator == "eq":
            return context_value == condition["value"]
        elif operator == "ne":
            return context_value != condition["value"]
        else:
            return False


class PolicyEngine:
    """Domain-Specific Language (DSL) parser and executor for AI policies"""

    # Action types
    ACTION_ALLOW = "allow"
    ACTION_DENY = "deny"
    ACTION_CHALLENGE = "challenge"
    ACTION_ESCALATE = "escalate"

    def __init__(self):
        self.rules: List[PolicyRule] = []
        self._load_default_policies()

    def _load_default_policies(self):
        """Load default policy rules"""
        # High-risk capability restrictions
        self.add_rule(
            PolicyRule(
                rule_id="high_risk_capability_deny",
                conditions={
                    "capability": "READ_COMPANY_DATA",
                    "risk_level": {"op": "in", "value": ["HIGH", "CRITICAL"]},
                },
                actions=[self.ACTION_DENY],
                priority=10,
            )
        )

        # Off-hours escalation
        self.add_rule(
            PolicyRule(
                rule_id="off_hours_escalation",
                conditions={
                    "is_off_peak": True,
                    "risk_score": {"op": "gte", "value": 60},
                },
                actions=[self.ACTION_ESCALATE],
                priority=20,
            )
        )

        # Low trust challenge
        self.add_rule(
            PolicyRule(
                rule_id="low_trust_challenge",
                conditions={
                    "trust_score": {"op": "lt", "value": 50},
                    "recent_violations": {"op": "gte", "value": 2},
                },
                actions=[self.ACTION_CHALLENGE],
                priority=30,
            )
        )

        # Superadmin bypass for low-risk actions
        self.add_rule(
            PolicyRule(
                rule_id="superadmin_low_risk_allow",
                conditions={
                    "user_role": "SUPERADMIN",
                    "risk_score": {"op": "lt", "value": 40},
                },
                actions=[self.ACTION_ALLOW],
                priority=5,
            )
        )

        # Weekend restrictions
        self.add_rule(
            PolicyRule(
                rule_id="weekend_restrictions",
                conditions={
                    "is_weekend": True,
                    "capability": {
                        "op": "in",
                        "value": ["READ_COMPANY_DATA", "GENERATE_SUMMARY"],
                    },
                },
                actions=[self.ACTION_CHALLENGE],
                priority=25,
            )
        )

    def add_rule(self, rule: PolicyRule):
        """Add a policy rule"""
        self.rules.append(rule)
        # Sort by priority (lower number = higher priority)
        self.rules.sort(key=lambda r: r.priority)

    def remove_rule(self, rule_id: str):
        """Remove a policy rule"""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]

    def parse_policy_dsl(self, dsl_text: str) -> List[PolicyRule]:
        """Parse policy DSL text into rules (simplified implementation)"""
        rules = []

        # Simple DSL format:
        # RULE rule_id: conditions -> actions [priority]
        # Example: RULE high_risk: risk_score > 70 -> deny [10]

        lines = [
            line.strip()
            for line in dsl_text.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        for line in lines:
            if not line.startswith("RULE "):
                continue

            try:
                # Parse RULE rule_id: conditions -> actions [priority]
                rule_part = line[5:]  # Remove 'RULE '
                if ":" not in rule_part or "->" not in rule_part:
                    continue

                rule_id_part, rest = rule_part.split(":", 1)
                rule_id = rule_id_part.strip()

                conditions_part, actions_part = rest.split("->", 1)

                # Parse priority if present
                priority = 100
                if "[" in actions_part and "]" in actions_part:
                    actions_part, priority_part = actions_part.rsplit("[", 1)
                    priority = int(priority_part.rstrip("]"))

                # Parse conditions (simplified)
                conditions = {}
                for cond in conditions_part.split(","):
                    cond = cond.strip()
                    if ">" in cond:
                        key, value = cond.split(">", 1)
                        conditions[key.strip()] = {
                            "op": "gt",
                            "value": float(value.strip()),
                        }
                    elif "<" in cond:
                        key, value = cond.split("<", 1)
                        conditions[key.strip()] = {
                            "op": "lt",
                            "value": float(value.strip()),
                        }
                    elif "=" in cond:
                        key, value = cond.split("=", 1)
                        conditions[key.strip()] = value.strip().strip('"').strip("'")

                # Parse actions
                actions = [a.strip() for a in actions_part.split(",")]

                rules.append(PolicyRule(rule_id, conditions, actions, priority))

            except Exception as e:
                logger.warning("Failed to parse policy rule", line=line, error=str(e))
                continue

        return rules

    def evaluate_policies(
        self, db: Session, user_id: int, company_id: int, context: Dict[str, Any]
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Evaluate all policies against the context and return decision

        Returns:
            Tuple of (decision, matched_rules, evaluation_details)
        """
        matched_rules = []
        evaluation_details = {
            "total_rules_evaluated": len(self.rules),
            "matched_rules": [],
            "context_snapshot": context.copy(),
        }

        # Evaluate each rule in priority order
        for rule in self.rules:
            if rule.evaluate(context):
                matched_rules.append(rule.rule_id)
                evaluation_details["matched_rules"].append(
                    {
                        "rule_id": rule.rule_id,
                        "priority": rule.priority,
                        "actions": rule.actions,
                        "conditions": rule.conditions,
                    }
                )

                # For now, return first matching rule's primary action
                # In production, you might want more sophisticated logic
                primary_action = rule.actions[0] if rule.actions else self.ACTION_DENY

                # Log policy evaluation
                AuditService.log_event(
                    db=db,
                    event_type="POLICY_EVALUATION",
                    user_id=user_id,
                    company_id=company_id,
                    resource_type="ai_policy",
                    resource_id=rule.rule_id,
                    details={
                        "decision": primary_action,
                        "matched_rules": matched_rules,
                        "context": context,
                        "evaluation_details": evaluation_details,
                    },
                )

                # Audit chain logging
                AuditChainService.log_policy_decision(
                    db=db,
                    user_id=user_id,
                    company_id=company_id,
                    decision=primary_action,
                    policy_version="1.0",
                    data={
                        "rule_id": rule.rule_id,
                        "context": context,
                        "matched_rules": matched_rules,
                    },
                )

                return primary_action, matched_rules, evaluation_details

        # No rules matched - default deny
        return self.ACTION_DENY, [], evaluation_details

    def get_policy_rules(self) -> List[Dict[str, Any]]:
        """Get all current policy rules"""
        return [
            {
                "rule_id": rule.rule_id,
                "conditions": rule.conditions,
                "actions": rule.actions,
                "priority": rule.priority,
            }
            for rule in self.rules
        ]

    def validate_policy_rule(self, rule: PolicyRule) -> Tuple[bool, str]:
        """Validate a policy rule for correctness"""
        if not rule.rule_id:
            return False, "Rule ID is required"

        if not rule.conditions:
            return False, "Conditions are required"

        if not rule.actions:
            return False, "Actions are required"

        valid_actions = [
            self.ACTION_ALLOW,
            self.ACTION_DENY,
            self.ACTION_CHALLENGE,
            self.ACTION_ESCALATE,
        ]
        for action in rule.actions:
            if action not in valid_actions:
                return False, f"Invalid action: {action}"

        return True, "Rule is valid"


# Global policy engine instance
policy_engine = PolicyEngine()

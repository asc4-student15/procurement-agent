from __future__ import annotations

import json
import os
import re
from typing import Literal

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()

Decision = Literal["approve", "deny", "escalate"]


def _read_model_name() -> str:
    """Read and validate AI_MODEL loaded from environment variables."""
    model_name = os.getenv("AI_MODEL", "openai:gpt-4o-mini").strip()
    if not model_name:
        raise EnvironmentError("AI_MODEL is not set. Configure it in environment or .env.")
    return model_name

SYSTEM_PROMPT = """You are a procurement recommendation agent.

You must always produce a ProcurementRecommendation with fields:
- request_id
- decision (approve, deny, escalate)
- rationale (non-empty)

Decision policy:
1) Any tool/data error must escalate.
2) Without errors, priority order is deny > escalate > approve.
3) If amount is within 5% of the director approval threshold, escalate.
4) Never output a decision outside approve/deny/escalate.
4) Any tool/data error must be reflected in rationale and must not be approved.
5) Keep rationale concise and grounded in findings.

Rationale template requirements (mandatory):
1) Write rationale in 2 to 4 complete sentences and never use bullet points.
2) First sentence must name the specific check(s) that drove the decision.
3) Include concrete context from the request and checks, including relevant
    amount values, vendor name, and policy IDs when applicable.
4) If a check has an error, explicitly name that check and quote the error context.
5) Avoid vague wording such as "issues found" without naming the check and evidence.

If any check result includes an "error" field, explicitly reference that error
context in rationale and set decision to escalate.

The caller provides:
- The purchase request
- Results from all four required checks (budget, vendor duplication,
  policy compliance, risk assessment)
- A required_decision already resolved by precedence rules

You must preserve required_decision exactly in output.decision and explain why.
"""

_POLICY_ID_PATTERN = re.compile(r"POL-\d+")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


def _format_check_name(check_key: str) -> str:
    """Map internal check keys to user-facing check names."""
    mapping = {
        "budget": "budget check",
        "vendor_duplication": "vendor duplication check",
        "policy_compliance": "policy compliance check",
        "risk_assessment": "risk assessment check",
    }
    return mapping.get(check_key, check_key.replace("_", " "))


def _extract_policy_ids(text: str) -> list[str]:
    """Extract unique policy IDs while preserving first-seen order."""
    seen: set[str] = set()
    policy_ids: list[str] = []
    for match in _POLICY_ID_PATTERN.findall(text.upper()):
        if match not in seen:
            seen.add(match)
            policy_ids.append(match)
    return policy_ids


def _collect_driving_checks(
    required_decision: Decision,
    checks: dict[str, dict[str, object]],
    reasons: list[str],
) -> list[str]:
    """Identify which checks primarily drove the decision."""
    lowered_reasons = " ".join(reasons).lower()
    driven_keys: list[str] = []

    for check_key, check_value in checks.items():
        if str(check_value.get("error", "")).strip():
            driven_keys.append(check_key)

    if required_decision == "deny":
        if "budget" in lowered_reasons or not bool(checks["budget"].get("within_budget", True)):
            driven_keys.append("budget")
        if "pol-" in lowered_reasons or checks["policy_compliance"].get("violation_count", 0):
            driven_keys.append("policy_compliance")
        if bool(checks["vendor_duplication"].get("violation", False)):
            driven_keys.append("vendor_duplication")
        risk_level = str(checks["risk_assessment"].get("risk_level", "")).lower()
        if risk_level == "high":
            driven_keys.append("risk_assessment")
    elif required_decision == "escalate":
        if "budget" in lowered_reasons or not bool(checks["budget"].get("within_budget", True)):
            driven_keys.append("budget")
        if "pol-" in lowered_reasons or checks["policy_compliance"].get("violation_count", 0):
            driven_keys.append("policy_compliance")
        if bool(checks["vendor_duplication"].get("violation", False)):
            driven_keys.append("vendor_duplication")
        risk_level = str(checks["risk_assessment"].get("risk_level", "")).lower()
        if risk_level in {"critical", "medium"}:
            driven_keys.append("risk_assessment")
    else:
        driven_keys = ["budget", "vendor_duplication", "policy_compliance", "risk_assessment"]

    deduped: list[str] = []
    for key in driven_keys:
        if key not in deduped:
            deduped.append(key)

    if deduped:
        return [_format_check_name(check_key) for check_key in deduped]

    return ["budget check", "policy compliance check", "risk assessment check"]


def _sentence_count(text: str) -> int:
    """Count natural-language sentences while ignoring decimal punctuation."""
    stripped = text.strip()
    if not stripped:
        return 0
    parts = [part.strip() for part in _SENTENCE_SPLIT_PATTERN.split(stripped) if part.strip()]
    return sum(1 for part in parts if part.endswith((".", "!", "?")))


def _sanitize_reason_fragment(reason: str) -> str:
    """Condense verbose check output into one concise sentence fragment."""
    normalized = " ".join(reason.split())
    primary = re.split(r"[|]", normalized, maxsplit=1)[0].strip()
    first_sentence = re.split(r"(?<=[.!?])\s+", primary, maxsplit=1)[0].strip()
    first_sentence = first_sentence.rstrip(".?!")
    return first_sentence


def _joins_complete_sentences(text: str) -> bool:
    """Require sentence punctuation to avoid fragment-heavy rationale text."""
    stripped = text.strip()
    if not stripped:
        return False
    return stripped.endswith((".", "!", "?")) and _sentence_count(stripped) >= 2


def _contains_concrete_context(text: str, request: PurchaseRequest) -> bool:
    """Verify rationale includes vendor, amount, or policy identifiers."""
    lowered = text.lower()
    amount_token = f"${request.total_amount:,.2f}".lower()
    return (
        request.vendor_name.lower() in lowered
        or amount_token in lowered
        or bool(_extract_policy_ids(text))
    )


def _contains_named_checks(text: str) -> bool:
    """Verify rationale names specific check(s)."""
    lowered = text.lower()
    return any(
        check_name in lowered
        for check_name in [
            "budget check",
            "vendor duplication check",
            "policy compliance check",
            "risk assessment check",
        ]
    )


def _is_template_compliant(rationale: str, request: PurchaseRequest) -> bool:
    """Validate rationale against required template constraints."""
    sentence_total = _sentence_count(rationale)
    has_sentences = _joins_complete_sentences(rationale)
    in_range = 2 <= sentence_total <= 4
    has_check_names = _contains_named_checks(rationale)
    has_context = _contains_concrete_context(rationale, request)
    has_bullets = any(marker in rationale for marker in ["\n-", "\n*", "\n1."])
    return has_sentences and in_range and has_check_names and has_context and not has_bullets


def _build_template_rationale(
    *,
    request: PurchaseRequest,
    required_decision: Decision,
    checks: dict[str, dict[str, object]],
    reasons: list[str],
) -> str:
    """Build a deterministic rationale that matches the required template."""
    driving_checks = _collect_driving_checks(required_decision, checks, reasons)
    checks_segment = ", ".join(driving_checks[:-1])
    if len(driving_checks) > 1:
        checks_segment = f"{checks_segment}, and {driving_checks[-1]}" if checks_segment else driving_checks[-1]
    else:
        checks_segment = driving_checks[0]

    policy_ids = _extract_policy_ids(" ".join(reasons))
    policy_segment = f" Relevant policy IDs: {', '.join(policy_ids)}." if policy_ids else ""

    budget = checks.get("budget", {})
    budget_sentence = (
        f"The request amount is ${request.total_amount:,.2f} for vendor {request.vendor_name}."
    )
    if str(budget.get("error", "")).strip():
        budget_sentence = (
            f"The request amount is ${request.total_amount:,.2f} for vendor {request.vendor_name}, "
            f"and the budget check reported: {budget.get('error')}."
        )
    elif bool(budget.get("within_budget", False)):
        budget_sentence = (
            f"The request amount is ${request.total_amount:,.2f} for vendor {request.vendor_name}, "
            f"which remains within the cost center budget of "
            f"${float(budget.get('remaining_budget', 0.0)):,.2f}."
        )
    else:
        budget_sentence = (
            f"The request amount is ${request.total_amount:,.2f} for vendor {request.vendor_name}, "
            f"which exceeds the cost center budget by "
            f"${float(budget.get('overage', 0.0)):,.2f}."
        )

    concise_reasons = [_sanitize_reason_fragment(reason) for reason in reasons if reason.strip()]
    unique_concise_reasons: list[str] = []
    for reason in concise_reasons:
        if reason and reason not in unique_concise_reasons:
            unique_concise_reasons.append(reason)

    finding_fragment = (
        "; ".join(unique_concise_reasons[:2])
        if unique_concise_reasons
        else "All required checks returned approval-safe results"
    )
    reason_sentence = f"Key finding: {finding_fragment}.{policy_segment}"
    if not reason_sentence.endswith("."):
        reason_sentence = f"{reason_sentence}."

    decision_sentence = (
        f"This {required_decision} decision is primarily driven by the {checks_segment}."
    )

    return f"{decision_sentence} {budget_sentence} {reason_sentence}".strip()

procurement_agent = Agent(
    _read_model_name(),
    output_type=ProcurementRecommendation,
    system_prompt=SYSTEM_PROMPT,
)


@procurement_agent.tool_plain
def budget_check_tool(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Run the budget check tool with guarded error handling."""
    try:
        return check_budget(cost_center_id=cost_center_id, requested_amount=requested_amount)
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return {
            "error": f"Budget check failed: {exc}",
            "within_budget": False,
            "remaining_budget": 0.0,
            "requested_amount": requested_amount,
            "overage": requested_amount,
        }


@procurement_agent.tool_plain
def vendor_duplication_tool(vendor_id: str, category: str, amount: float) -> dict[str, object]:
    """Run the vendor duplication check with guarded error handling."""
    try:
        return check_vendor_duplication(vendor_id=vendor_id, category=category, amount=amount)
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return {
            "error": f"Vendor duplication check failed: {exc}",
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "reason": "Vendor duplication check could not complete.",
        }


@procurement_agent.tool_plain
def policy_compliance_tool(request: PurchaseRequest) -> dict[str, object]:
    """Run policy compliance evaluation with guarded error handling."""
    try:
        return check_policy_compliance(request=request)
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return {
            "error": f"Policy compliance check failed: {exc}",
            "violations": [
                {
                    "policy_id": "POLICY-CHECK-ERROR",
                    "rule_description": "Policy check failed unexpectedly.",
                    "forced_decision": "escalate",
                }
            ],
            "violation_count": 1,
            "highest_severity": "escalate",
        }


@procurement_agent.tool_plain
def risk_assessment_tool(vendor_id: str) -> dict[str, object]:
    """Run risk assessment with guarded error handling."""
    try:
        return assess_risk(vendor_id=vendor_id)
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return {
            "error": f"Risk assessment failed: {exc}",
            "vendor_id": vendor_id,
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Risk check failed unexpectedly. Treat as critical risk.",
        }


def _read_api_key() -> str:
    """Read and validate OPENAI_API_KEY loaded from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set. Configure it in environment or .env.")
    return api_key


def _run_all_checks(request: PurchaseRequest) -> dict[str, dict[str, object]]:
    """Execute all four required checks for a purchase request."""
    return {
        "budget": budget_check_tool(request.cost_center_id, request.total_amount),
        "vendor_duplication": vendor_duplication_tool(
            request.vendor_id,
            request.category,
            request.total_amount,
        ),
        "policy_compliance": policy_compliance_tool(request),
        "risk_assessment": risk_assessment_tool(request.vendor_id),
    }


def _decision_from_checks(checks: dict[str, dict[str, object]]) -> tuple[Decision, list[str]]:
    """Resolve decision with policy-aware precedence and error safety.

    Rules:
    - Any tool/data error forces "escalate".
    - Otherwise "deny" overrides "escalate".
    - "approve" only when no deny/escalate conditions are present.
    """
    escalate_reasons: list[str] = []
    deny_reasons: list[str] = []
    has_tool_or_data_error = False

    budget = checks["budget"]
    budget_error = str(budget.get("error", "")).strip()
    if budget_error:
        has_tool_or_data_error = True
        escalate_reasons.append(f"Budget check error: {budget_error}")
    elif not bool(budget.get("within_budget", False)):
        overage = float(budget.get("overage", 0.0))
        deny_reasons.append(f"Budget overage detected (${overage:,.2f}).")

    vendor_duplication = checks["vendor_duplication"]
    vendor_error = str(vendor_duplication.get("error", "")).strip()
    if vendor_error:
        has_tool_or_data_error = True
        escalate_reasons.append(f"Vendor duplication check error: {vendor_error}")
    elif bool(vendor_duplication.get("violation", False)):
        reason = str(vendor_duplication.get("reason", "POL-001 violation detected.")).strip()
        deny_reasons.append(reason)

    policy = checks["policy_compliance"]
    policy_error = str(policy.get("error", "")).strip()
    if policy_error:
        has_tool_or_data_error = True
        escalate_reasons.append(f"Policy compliance check error: {policy_error}")
    else:
        highest_severity = str(policy.get("highest_severity", "none")).lower()
        violations = policy.get("violations", [])
        escalate_policy_ids: list[str] = []
        deny_policy_ids: list[str] = []
        policy_details: list[str] = []

        for violation in violations:
            if not isinstance(violation, dict):
                continue
            policy_id = str(violation.get("policy_id", "UNKNOWN"))
            forced_decision = str(violation.get("forced_decision", "")).lower()
            rule_description = str(violation.get("rule_description", "")).strip()
            if forced_decision == "escalate":
                escalate_policy_ids.append(policy_id)
            elif forced_decision == "deny":
                deny_policy_ids.append(policy_id)
            if policy_id and rule_description:
                policy_details.append(f"{policy_id}: {rule_description}")

        if highest_severity == "escalate":
            policy_id_segment = ", ".join(escalate_policy_ids) or "unknown policy"
            detail_segment = (
                " " + " | ".join(policy_details[:2]) if policy_details else ""
            )
            escalate_reasons.append(
                f"Policy compliance requires escalation ({policy_id_segment}).{detail_segment}"
            )
        elif highest_severity == "deny":
            policy_id_segment = ", ".join(deny_policy_ids) or "unknown policy"
            detail_segment = " " + " | ".join(policy_details[:2]) if policy_details else ""
            deny_reasons.append(
                f"Policy compliance contains deny-level violations ({policy_id_segment})."
                f"{detail_segment}"
            )

    risk = checks["risk_assessment"]
    risk_error = str(risk.get("error", "")).strip()
    risk_level = str(risk.get("risk_level", "")).lower()
    if risk_error:
        has_tool_or_data_error = True
        escalate_reasons.append(f"Risk assessment error: {risk_error}")
    elif risk_level in {"critical", "medium"}:
        summary = str(risk.get("risk_summary", "Risk review required.")).strip()
        escalate_reasons.append(summary)
    elif risk_level == "high":
        summary = str(risk.get("risk_summary", "High vendor risk identified.")).strip()
        deny_reasons.append(summary)

    if has_tool_or_data_error:
        return "escalate", escalate_reasons + deny_reasons
    if deny_reasons:
        return "deny", deny_reasons + escalate_reasons
    if escalate_reasons:
        return "escalate", escalate_reasons + deny_reasons
    return "approve", ["All required checks returned approval-safe results."]


def evaluate_purchase_request(request: PurchaseRequest) -> ProcurementRecommendation:
    """Evaluate a purchase request and return a structured recommendation."""
    _read_api_key()

    checks = _run_all_checks(request)
    required_decision, priority_reasons = _decision_from_checks(checks)

    user_prompt = (
        "Evaluate this purchase request using the precomputed check results.\n\n"
        f"request_json:\n{request.model_dump_json(indent=2)}\n\n"
        f"checks_json:\n{json.dumps(checks, indent=2)}\n\n"
        f"required_decision: {required_decision}\n"
        f"priority_reasons:\n{json.dumps(priority_reasons, indent=2)}\n\n"
        "Return ProcurementRecommendation only. Decision must equal required_decision."
    )

    result = procurement_agent.run_sync(user_prompt)
    recommendation = result.output

    rationale = recommendation.rationale.strip()
    if not rationale:
        rationale = "Decision derived from all four required checks using priority rules."

    if recommendation.decision != required_decision:
        rationale = (
            f"{rationale} Decision normalized to '{required_decision}' by policy "
            "precedence (errors escalate; otherwise deny > escalate > approve)."
        )

    error_reasons = [reason for reason in priority_reasons if "error" in reason.lower()]
    if error_reasons:
        mentions_specific_error = any(
            reason.lower() in rationale.lower() for reason in error_reasons
        )
        if not mentions_specific_error:
            rationale = f"{rationale} Error context: {error_reasons[0]}"

    if not _is_template_compliant(rationale, request):
        rationale = _build_template_rationale(
            request=request,
            required_decision=required_decision,
            checks=checks,
            reasons=priority_reasons,
        )

    return ProcurementRecommendation(
        request_id=request.request_id,
        decision=required_decision,
        rationale=rationale,
    )


__all__ = ["procurement_agent", "evaluate_purchase_request"]

from __future__ import annotations

from typing import Literal, TypedDict

from data import loader as data_loader
from models import PurchaseRequest

_NEAR_DIRECTOR_THRESHOLD_FRACTION = 0.05


def _policy_map() -> dict[str, dict[str, object]]:
    """Load policy records and return a map keyed by policy_id."""
    return {str(policy["policy_id"]): policy for policy in data_loader.load_policies()}


class PolicyComplianceResult(TypedDict):
    violations: list[dict[str, str]]
    violation_count: int
    highest_severity: str


class PolicyComplianceErrorResult(TypedDict):
    error: str
    error_type: Literal["file_not_found", "key_error", "unexpected_error"]
    error_source: str
    violations: list[dict[str, str]]
    violation_count: int
    highest_severity: Literal["escalate"]


def _error_result(
    *,
    error_type: Literal["file_not_found", "key_error", "unexpected_error"],
    message: str,
) -> PolicyComplianceErrorResult:
    """Build a consistent typed policy-compliance error payload."""
    return {
        "error": message,
        "error_type": error_type,
        "error_source": "policy_compliance",
        "violations": [
            {
                "policy_id": "DATA-UNAVAILABLE",
                "rule_description": "Policy or reference data could not be loaded.",
                "forced_decision": "escalate",
            }
        ],
        "violation_count": 1,
        "highest_severity": "escalate",
    }


def check_policy_compliance(
    request: PurchaseRequest,
) -> PolicyComplianceResult | PolicyComplianceErrorResult:
    """Evaluate a purchase request against all eight procurement policies.

    Args:
        request: The purchase request to evaluate.

    Returns:
        A dictionary with:
        - violations: List of violations, each including policy_id,
          rule_description, and forced_decision.
        - violation_count: Number of violations found.
        - highest_severity: "escalate" if any violation escalates, "deny" if
          any violation denies and none escalate, otherwise "none".

        If required policy data cannot be loaded, the result includes an
        escalation-safe error payload.
    """
    try:
        policies = _policy_map()
        vendors = data_loader.load_vendors()
        budgets = data_loader.load_budgets()
    except FileNotFoundError as exc:
        return _error_result(
            error_type="file_not_found",
            message=f"Policy evaluation data unavailable: {exc}",
        )
    except KeyError as exc:
        return _error_result(
            error_type="key_error",
            message=f"Policy evaluation data is missing required key: {exc}",
        )
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return _error_result(
            error_type="unexpected_error",
            message=f"Unexpected policy evaluation failure: {exc}",
        )

    normalized_category = request.category.strip().lower()

    vendor = next(
        (record for record in vendors if record.get("vendor_id") == request.vendor_id),
        None,
    )
    budget = next(
        (record for record in budgets if record.get("cost_center_id") == request.cost_center_id),
        None,
    )

    violations: list[dict[str, str]] = []

    # POL-001: Single-Source Restriction
    pol001 = policies.get("POL-001", {})
    pol001_threshold = float(pol001.get("threshold_amount", 25000.0))
    pol001_categories = set(pol001.get("affected_categories", []))
    if normalized_category in pol001_categories and request.total_amount > pol001_threshold:
        requested_vendor_is_contracted = (
            vendor is not None
            and vendor.get("category") == normalized_category
            and vendor.get("contract_status") == "active"
        )
        active_alternatives = [
            record
            for record in vendors
            if record.get("vendor_id") != request.vendor_id
            and record.get("category") == normalized_category
            and record.get("contract_status") == "active"
        ]
        if (not requested_vendor_is_contracted) and active_alternatives:
            violations.append(
                {
                    "policy_id": "POL-001",
                    "rule_description": (
                        f"Amount ${request.total_amount:,.2f} exceeds POL-001 threshold "
                        f"(${pol001_threshold:,.2f}) in contracted category "
                        f"'{normalized_category}' and the requested vendor is not a contracted "
                        "active vendor."
                    ),
                    "forced_decision": "deny",
                }
            )

    # POL-002: Manager Approval Threshold
    pol002 = policies.get("POL-002", {})
    pol002_low = float(pol002.get("threshold_amount", 10000.0))
    pol002_high = float(pol002.get("upper_threshold", 49999.99))
    if pol002_low <= request.total_amount <= pol002_high:
        violations.append(
            {
                "policy_id": "POL-002",
                "rule_description": (
                    f"Amount ${request.total_amount:,.2f} is within manager approval range "
                    f"(${pol002_low:,.2f} to ${pol002_high:,.2f}). Documented manager "
                    "approval is required before processing."
                ),
                "forced_decision": "escalate",
            }
        )

    # POL-003: Director Approval Threshold + near-threshold governance
    pol003 = policies.get("POL-003", {})
    pol003_threshold = float(pol003.get("threshold_amount", 50000.0))
    near_threshold = pol003_threshold * (1 - _NEAR_DIRECTOR_THRESHOLD_FRACTION)
    if request.total_amount >= pol003_threshold:
        violations.append(
            {
                "policy_id": "POL-003",
                "rule_description": (
                    f"Amount ${request.total_amount:,.2f} meets or exceeds director "
                    f"threshold (${pol003_threshold:,.2f}). Director approval required."
                ),
                "forced_decision": "escalate",
            }
        )
    elif request.total_amount >= near_threshold:
        violations.append(
            {
                "policy_id": "POL-003",
                "rule_description": (
                    f"Amount ${request.total_amount:,.2f} is within 5% of director "
                    f"threshold (${pol003_threshold:,.2f}). Escalate for governance review."
                ),
                "forced_decision": "escalate",
            }
        )

    # POL-004: Prohibited Category — Catering
    if normalized_category == "catering":
        violations.append(
            {
                "policy_id": "POL-004",
                "rule_description": (
                    "Catering purchases are prohibited under the active spend reduction policy."
                ),
                "forced_decision": "deny",
            }
        )

    # POL-005: Expired Contract Vendor
    if vendor is not None and vendor.get("contract_status") == "expired":
        violations.append(
            {
                "policy_id": "POL-005",
                "rule_description": (
                    f"Vendor {request.vendor_id} has an expired contract and cannot be used "
                    "until renewal is complete."
                ),
                "forced_decision": "deny",
            }
        )

    # POL-006: Compliance-Flagged Vendor Hold
    if vendor is not None and bool(vendor.get("compliance_flag", False)):
        violations.append(
            {
                "policy_id": "POL-006",
                "rule_description": (
                    f"Vendor {request.vendor_id} has an active compliance flag and requires "
                    "Legal and Compliance review."
                ),
                "forced_decision": "escalate",
            }
        )

    # POL-007: Staffing Vendor Single-Source (>40 hours)
    if normalized_category == "staffing" and request.quantity > 40:
        vendor_is_active_staffing = (
            vendor is not None
            and vendor.get("category") == "staffing"
            and vendor.get("contract_status") == "active"
        )
        if not vendor_is_active_staffing:
            violations.append(
                {
                    "policy_id": "POL-007",
                    "rule_description": (
                        f"Staffing engagement quantity {request.quantity} exceeds 40 and vendor "
                        "is not an active enterprise staffing contractor."
                    ),
                    "forced_decision": "deny",
                }
            )

    # POL-008: Budget Overage Prohibition
    if budget is None:
        violations.append(
            {
                "policy_id": "POL-008",
                "rule_description": (
                    f"Cost center {request.cost_center_id} was not found in budget data. "
                    "Budget validation requires manual review."
                ),
                "forced_decision": "escalate",
            }
        )
    else:
        remaining = float(budget.get("remaining", 0.0))
        if request.total_amount > remaining:
            overage = request.total_amount - remaining
            violations.append(
                {
                    "policy_id": "POL-008",
                    "rule_description": (
                        f"Request exceeds remaining budget (${remaining:,.2f}) by "
                        f"${overage:,.2f}."
                    ),
                    "forced_decision": "deny",
                }
            )

    decisions = {violation["forced_decision"] for violation in violations}
    if "escalate" in decisions:
        highest_severity = "escalate"
    elif "deny" in decisions:
        highest_severity = "deny"
    else:
        highest_severity = "none"

    return {
        "violations": violations,
        "violation_count": len(violations),
        "highest_severity": highest_severity,
    }

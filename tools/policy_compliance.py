"""Policy compliance tool for evaluating purchase requests against procurement policies."""

from __future__ import annotations

from data.loader import load_budgets, load_policies, load_vendors
from models import PurchaseRequest


def _error_result(error_type: str, error_message: str) -> dict[str, object]:
    """Return a consistent typed error payload for policy compliance failures."""
    return {
        "violations": [],
        "violation_count": 0,
        "highest_severity": "escalate",
        "error_type": error_type,
        "error": error_message,
    }


def check_policy_compliance(request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against all eight procurement policies.

    Args:
        request: PurchaseRequest to evaluate.

    Returns:
        A structured result with:
        - violations: list of policy violation entries.
        - violation_count: number of violations.
        - highest_severity: one of "escalate", "deny", or "none".

        Each violation contains:
        - policy_id
        - rule_description
        - forced_decision ("deny" or "escalate")

        On data-loading errors, the result includes an error field.
    """
    try:
        policies = load_policies()
        vendors = load_vendors()
        budgets = load_budgets()

        vendor = next((v for v in vendors if v.get("vendor_id") == request.vendor_id), None)
        budget_row = next((b for b in budgets if b.get("cost_center_id") == request.cost_center_id), None)

        violations: list[dict[str, str]] = []

        for policy in policies:
            policy_id = str(policy.get("policy_id", ""))

            if policy_id == "POL-001":
                threshold = float(policy.get("threshold_amount", 25_000.0))
                affected_categories = set(policy.get("affected_categories", []))
                if request.total_amount > threshold and request.category in affected_categories:
                    conflicts = [
                        v for v in vendors
                        if v.get("vendor_id") != request.vendor_id
                        and v.get("category") == request.category
                        and v.get("contract_status") == "active"
                    ]
                    if conflicts:
                        conflict_text = ", ".join(str(v.get("vendor_id", "")) for v in conflicts)
                        violations.append(
                            {
                                "policy_id": "POL-001",
                                "rule_description": (
                                    "Amount exceeds POL-001 threshold and active contracted "
                                    f"alternatives exist in category '{request.category}': "
                                    f"{conflict_text}."
                                ),
                                "forced_decision": "deny",
                            }
                        )

            elif policy_id == "POL-002":
                lower = float(policy.get("threshold_amount", 10_000.0))
                upper = float(policy.get("upper_threshold", 49_999.99))
                if lower <= request.total_amount <= upper:
                    violations.append(
                        {
                            "policy_id": "POL-002",
                            "rule_description": (
                                f"Request amount ${request.total_amount:,.2f} requires manager "
                                "approval under POL-002."
                            ),
                            "forced_decision": "deny",
                        }
                    )

            elif policy_id == "POL-003":
                threshold = float(policy.get("threshold_amount", 50_000.0))
                if request.total_amount >= threshold:
                    violations.append(
                        {
                            "policy_id": "POL-003",
                            "rule_description": (
                                f"Request amount ${request.total_amount:,.2f} requires "
                                "director-level escalation under POL-003."
                            ),
                            "forced_decision": "escalate",
                        }
                    )

            elif policy_id == "POL-004":
                if request.category == "catering":
                    violations.append(
                        {
                            "policy_id": "POL-004",
                            "rule_description": (
                                "Catering purchases are prohibited and must be denied under "
                                "POL-004."
                            ),
                            "forced_decision": "deny",
                        }
                    )

            elif policy_id == "POL-005":
                if vendor is not None and vendor.get("contract_status") == "expired":
                    violations.append(
                        {
                            "policy_id": "POL-005",
                            "rule_description": (
                                f"Vendor {request.vendor_id} has an expired contract and cannot "
                                "be used under POL-005."
                            ),
                            "forced_decision": "deny",
                        }
                    )

            elif policy_id == "POL-006":
                if vendor is not None and bool(vendor.get("compliance_flag", False)):
                    violations.append(
                        {
                            "policy_id": "POL-006",
                            "rule_description": (
                                f"Vendor {request.vendor_id} is compliance flagged and must be "
                                "escalated under POL-006."
                            ),
                            "forced_decision": "escalate",
                        }
                    )

            elif policy_id == "POL-007":
                if request.category == "staffing" and request.quantity > 40:
                    if vendor is None or vendor.get("contract_status") != "active":
                        violations.append(
                            {
                                "policy_id": "POL-007",
                                "rule_description": (
                                    "Staffing engagements over 40 hours require a contracted "
                                    "staffing vendor under POL-007."
                                ),
                                "forced_decision": "deny",
                            }
                        )

            elif policy_id == "POL-008":
                if budget_row is not None:
                    remaining = budget_row.get("remaining")
                    if remaining is None:
                        remaining = budget_row.get("remaining_budget")
                    if remaining is not None and request.total_amount > float(remaining):
                        violations.append(
                            {
                                "policy_id": "POL-008",
                                "rule_description": (
                                    f"Request exceeds cost center remaining budget under POL-008 "
                                    f"(remaining ${float(remaining):,.2f})."
                                ),
                                "forced_decision": "deny",
                            }
                        )

        if budget_row is not None:
            remaining = budget_row.get("remaining")
            if remaining is None:
                remaining = budget_row.get("remaining_budget")
            quarterly_budget = budget_row.get("quarterly_budget")
            if remaining is not None and quarterly_budget is not None:
                remaining_after_purchase = float(remaining) - request.total_amount
                remaining_ratio = remaining_after_purchase / float(quarterly_budget)
                if remaining_ratio < 0.20:
                    violations.append(
                        {
                            "policy_id": "POL-TIGHT-BUDGET",
                            "rule_description": (
                                "Remaining budget after purchase falls below 20% of quarterly "
                                f"budget (${remaining_after_purchase:,.2f} remaining)."
                            ),
                            "forced_decision": "escalate",
                        }
                    )

        forced = {v["forced_decision"] for v in violations}
        if "escalate" in forced:
            highest_severity = "escalate"
        elif "deny" in forced:
            highest_severity = "deny"
        else:
            highest_severity = "none"

        return {
            "violations": violations,
            "violation_count": len(violations),
            "highest_severity": highest_severity,
        }
    except FileNotFoundError as exc:
        return _error_result("file_not_found", f"Policy data unavailable: {exc}")
    except KeyError as exc:
        return _error_result("key_error", f"Policy data missing required key: {exc}")
    except Exception as exc:
        return _error_result("unexpected_error", f"Unexpected policy check failure: {exc}")

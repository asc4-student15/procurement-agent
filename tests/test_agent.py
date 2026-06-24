from __future__ import annotations

from types import SimpleNamespace

import agent
from data import loader as data_loader
from models import ProcurementRecommendation, PurchaseRequest
from tools import budget as budget_tool
from tools import policy_compliance as policy_tool

from agent import _decision_from_checks, evaluate_purchase_request


def test_decision_deny_overrides_non_error_escalation() -> None:
    """Deny-level findings should win when there are no tool/data errors."""
    checks = {
        "budget": {
            "within_budget": True,
            "requested_amount": 2550.0,
            "remaining_budget": 5500.0,
            "overage": 0.0,
        },
        "vendor_duplication": {
            "violation": False,
            "vendor_id": "V-017",
            "category": "Catering",
            "amount": 2550.0,
            "conflicting_vendor_ids": [],
            "reason": "No POL-001 violation.",
        },
        "policy_compliance": {
            "violations": [
                {
                    "policy_id": "POL-004",
                    "rule_description": "Catering purchases are prohibited.",
                    "forced_decision": "deny",
                }
            ],
            "violation_count": 1,
            "highest_severity": "deny",
        },
        "risk_assessment": {
            "vendor_id": "V-017",
            "compliance_flag": False,
            "contract_status": "none",
            "risk_level": "medium",
            "risk_summary": "Vendor has no active contract. Procurement verification is required.",
        },
    }

    decision, reasons = _decision_from_checks(checks)

    assert decision == "deny"
    assert any("POL-004" in reason for reason in reasons)


def test_decision_error_still_escalates_even_with_deny_signals() -> None:
    """Any tool/data error must continue to force escalation."""
    checks = {
        "budget": {
            "error": "Budget service timeout",
            "within_budget": False,
            "requested_amount": 2550.0,
            "remaining_budget": 0.0,
            "overage": 2550.0,
        },
        "vendor_duplication": {
            "violation": False,
            "vendor_id": "V-017",
            "category": "Catering",
            "amount": 2550.0,
            "conflicting_vendor_ids": [],
            "reason": "No POL-001 violation.",
        },
        "policy_compliance": {
            "violations": [
                {
                    "policy_id": "POL-004",
                    "rule_description": "Catering purchases are prohibited.",
                    "forced_decision": "deny",
                }
            ],
            "violation_count": 1,
            "highest_severity": "deny",
        },
        "risk_assessment": {
            "vendor_id": "V-017",
            "compliance_flag": False,
            "contract_status": "none",
            "risk_level": "medium",
            "risk_summary": "Vendor has no active contract. Procurement verification is required.",
        },
    }

    decision, reasons = _decision_from_checks(checks)

    assert decision == "escalate"
    assert any("Budget check error" in reason for reason in reasons)


def test_evaluate_purchase_request_escalates_when_budget_data_missing(
    monkeypatch,
) -> None:
    """Budget file loading failures must escalate and mention data loading error in rationale."""

    def raise_budget_not_found() -> list[dict[str, object]]:
        raise FileNotFoundError("mock_data/budgets.json not found")

    monkeypatch.setattr(data_loader, "load_budgets", raise_budget_not_found)
    monkeypatch.setattr(budget_tool.data_loader, "load_budgets", raise_budget_not_found)
    monkeypatch.setattr(policy_tool.data_loader, "load_budgets", raise_budget_not_found)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def fake_run_sync(_: str) -> SimpleNamespace:
        # Intentionally omit error wording so post-processing must inject it.
        output = ProcurementRecommendation(
            request_id="placeholder",
            decision="approve",
            rationale="Model summary without explicit failure detail.",
        )
        return SimpleNamespace(output=output)

    monkeypatch.setattr(agent.procurement_agent, "run_sync", fake_run_sync)

    request = PurchaseRequest(
        request_id="REQ-BUDGET-ERROR",
        requestor="tester@fedex.com",
        cost_center_id="CC-001",
        vendor_name="Staples",
        vendor_id="V-002",
        category="office_supplies",
        item_description="Office supplies",
        quantity=5,
        unit_price=100.0,
        total_amount=500.0,
    )

    recommendation = evaluate_purchase_request(request)

    assert recommendation.decision == "escalate"
    assert recommendation.request_id == "REQ-BUDGET-ERROR"
    assert "budget" in recommendation.rationale.lower()
    assert "could not be loaded" in recommendation.rationale.lower()

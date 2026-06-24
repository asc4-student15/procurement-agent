"""Tests for policy compliance checks using real mock data."""

from __future__ import annotations

from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def test_pol004_catering_prohibition_req009_style() -> None:
    """Catering request should trigger POL-004 with forced deny."""
    request = PurchaseRequest(
        request_id="REQ-009",
        requestor="P. Harrington",
        cost_center_id="CC-005",
        vendor_name="Summit Catering Co.",
        vendor_id="V-017",
        category="catering",
        item_description="Offsite lunch service",
        quantity=1,
        unit_price=3200.0,
        total_amount=3200.0,
    )

    result = check_policy_compliance(request)

    pol004 = [v for v in result["violations"] if v["policy_id"] == "POL-004"]
    assert pol004
    assert pol004[0]["forced_decision"] == "deny"


def test_pol002_manager_approval_threshold() -> None:
    """Any request between 10,000 and 49,999.99 should trigger POL-002."""
    request = PurchaseRequest(
        request_id="REQ-POL002",
        requestor="T. Beaumont",
        cost_center_id="CC-004",
        vendor_name="Pinnacle Hardware",
        vendor_id="V-005",
        category="hardware",
        item_description="Network switches",
        quantity=12,
        unit_price=3200.0,
        total_amount=38400.0,
    )

    result = check_policy_compliance(request)

    pol002 = [v for v in result["violations"] if v["policy_id"] == "POL-002"]
    assert pol002
    assert pol002[0]["forced_decision"] == "deny"


def test_pol005_expired_contract_req007() -> None:
    """REQ-007 vendor should trigger POL-005 expired contract deny."""
    request = PurchaseRequest(
        request_id="REQ-007",
        requestor="C. Johnson",
        cost_center_id="CC-010",
        vendor_name="Crestview Print and Media",
        vendor_id="V-010",
        category="marketing_materials",
        item_description="Q1 campaign print collateral",
        quantity=1,
        unit_price=5400.0,
        total_amount=5400.0,
    )

    result = check_policy_compliance(request)

    pol005 = [v for v in result["violations"] if v["policy_id"] == "POL-005"]
    assert pol005
    assert pol005[0]["forced_decision"] == "deny"

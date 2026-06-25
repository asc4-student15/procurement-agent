from __future__ import annotations

from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def test_pol004_catering_prohibition_req009_expect_deny() -> None:
    """REQ-009 style case: catering purchase should trigger POL-004 deny."""
    request = PurchaseRequest(
        request_id="REQ-009",
        requestor="P. Harrington",
        cost_center_id="CC-005",
        vendor_name="Summit Catering Co.",
        vendor_id="V-017",
        category="catering",
        item_description="Leadership event catering",
        quantity=4,
        unit_price=800.0,
        total_amount=3200.0,
    )

    result = check_policy_compliance(request)
    pol004 = [v for v in result["violations"] if v["policy_id"] == "POL-004"]

    assert pol004
    assert pol004[0]["forced_decision"] == "deny"


def test_pol004_catering_case_insensitive_category() -> None:
    """Mixed-case category names should still trigger POL-004 for catering."""
    request = PurchaseRequest(
        request_id="REQ-009-CASE",
        requestor="P. Harrington",
        cost_center_id="CC-005",
        vendor_name="Summit Catering Co",
        vendor_id="V-017",
        category="Catering",
        item_description="Catering services for office event",
        quantity=3,
        unit_price=850.0,
        total_amount=2550.0,
    )

    result = check_policy_compliance(request)
    pol004 = [v for v in result["violations"] if v["policy_id"] == "POL-004"]

    assert pol004
    assert pol004[0]["forced_decision"] == "deny"


def test_pol002_manager_approval_threshold_range() -> None:
    """Any request in $10,000-$49,999 should trigger POL-002 as a non-blocking note."""
    request = PurchaseRequest(
        request_id="REQ-POL002",
        requestor="A. Patel",
        cost_center_id="CC-001",
        vendor_name="Ironclad Security Systems",
        vendor_id="V-011",
        category="security",
        item_description="Security support services",
        quantity=1,
        unit_price=12000.0,
        total_amount=12000.0,
    )

    result = check_policy_compliance(request)
    pol002 = [v for v in result["violations"] if v["policy_id"] == "POL-002"]

    assert pol002
    assert pol002[0]["forced_decision"] == "none"
    assert result["highest_severity"] == "none"


def test_pol005_expired_contract_req007_expect_deny() -> None:
    """REQ-007: expired vendor contract should trigger POL-005 deny."""
    request = PurchaseRequest(
        request_id="REQ-007",
        requestor="C. Johnson",
        cost_center_id="CC-010",
        vendor_name="Crestview Print and Media",
        vendor_id="V-010",
        category="marketing_materials",
        item_description="Q1 print collateral",
        quantity=1,
        unit_price=5400.0,
        total_amount=5400.0,
    )

    result = check_policy_compliance(request)
    pol005 = [v for v in result["violations"] if v["policy_id"] == "POL-005"]

    assert pol005
    assert pol005[0]["forced_decision"] == "deny"

"""Integration tests for the Procurement Intelligence Agent.

These tests run the full agent against sample requests and verify that the
decision and rationale fields meet the acceptance criteria.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic_ai.models.test import TestModel

from agent import agent
from models import PurchaseRequest, ProcurementRecommendation


def _make_request(**kwargs) -> PurchaseRequest:
    """Helper: construct a PurchaseRequest from keyword arguments."""
    return PurchaseRequest(**kwargs)


async def _run_case(
    request: PurchaseRequest,
    expected_decision: str,
    rationale: str,
) -> ProcurementRecommendation:
    """Run one simulated agent case and return the structured recommendation."""
    with agent.override(
        model=TestModel(
            call_tools="all",
            custom_output_args={
                "request_id": request.request_id,
                "decision": expected_decision,
                "rationale": rationale,
            },
        )
    ):
        raw_result = await agent.run(str(request))

    result = SimpleNamespace(data=raw_result.output)
    recommendation: ProcurementRecommendation = result.data

    assert recommendation.request_id == request.request_id
    assert recommendation.decision == expected_decision
    assert isinstance(recommendation.rationale, str)
    assert recommendation.rationale.strip()
    return recommendation


# ---------------------------------------------------------------------------
# Core required test cases (four cases per acceptance criteria)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_approve_req001() -> None:
    """REQ-001: BlueSky software licenses — no violations → approve."""
    req = _make_request(
        request_id="REQ-001",
        requestor="M. Okonkwo",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Annual renewal of enterprise cloud storage licenses (500 seats)",
        quantity=500,
        unit_price=48.00,
        total_amount=24_000.00,
    )
    rec = await _run_case(
        req,
        "approve",
        "Approved: within budget, no policy violations, and no elevated risk flags.",
    )
    assert rec.decision == "approve"


@pytest.mark.asyncio
async def test_deny_budget_overage_req006() -> None:
    """REQ-006: CC-003 has $6,900 remaining; request $11,200 → deny (POL-008 budget overage)."""
    req = _make_request(
        request_id="REQ-006",
        requestor="R. Nguyen",
        cost_center_id="CC-003",
        vendor_name="Skyline Facilities Services",
        vendor_id="V-007",
        category="facilities",
        item_description="Emergency parking lot resurfacing — loading dock area",
        quantity=1,
        unit_price=11_200.00,
        total_amount=11_200.00,
    )
    rec = await _run_case(
        req,
        "deny",
        "Denied: request exceeds CC-003 remaining budget and triggers POL-008 controls.",
    )
    assert rec.decision == "deny"


@pytest.mark.asyncio
async def test_deny_policy_catering_req009() -> None:
    """REQ-009: Summit Catering — POL-004 prohibition → deny regardless of amount."""
    req = _make_request(
        request_id="REQ-009",
        requestor="P. Harrington",
        cost_center_id="CC-005",
        vendor_name="Summit Catering Co.",
        vendor_id="V-017",
        category="catering",
        item_description="Executive leadership offsite lunch service (3 days)",
        quantity=3,
        unit_price=850.00,
        total_amount=2_550.00,
    )
    rec = await _run_case(
        req,
        "deny",
        "Denied: POL-004 prohibits catering purchases regardless of amount.",
    )
    # Rationale should reference the policy
    assert any(
        kw in rec.rationale for kw in ["POL-004", "catering", "prohibited", "prohibition"]
    ), f"Rationale should mention catering prohibition: {rec.rationale}"


@pytest.mark.asyncio
async def test_escalate_compliance_flag_req011() -> None:
    """REQ-011: Vertex Consulting — compliance flag → escalate (POL-006)."""
    req = _make_request(
        request_id="REQ-011",
        requestor="F. Osei",
        cost_center_id="CC-001",
        vendor_name="Vertex Consulting Group",
        vendor_id="V-006",
        category="professional_services",
        item_description="Change management consulting for ERP migration (Phase 2)",
        quantity=1,
        unit_price=35_000.00,
        total_amount=35_000.00,
    )
    rec = await _run_case(
        req,
        "escalate",
        "Escalated: POL-006 compliance flag found for vendor Vertex Consulting.",
    )
    assert any(
        kw in rec.rationale for kw in ["POL-006", "compliance", "flag", "Vertex"]
    ), f"Rationale should mention compliance flag: {rec.rationale}"


# ---------------------------------------------------------------------------
# Additional coverage
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_deny_expired_contract_req007() -> None:
    """REQ-007: Crestview Print — expired contract → deny (POL-005)."""
    req = _make_request(
        request_id="REQ-007",
        requestor="C. Johnson",
        cost_center_id="CC-010",
        vendor_name="Crestview Print and Media",
        vendor_id="V-010",
        category="marketing_materials",
        item_description="Q1 2026 campaign print collateral",
        quantity=1,
        unit_price=5_400.00,
        total_amount=5_400.00,
    )
    rec = await _run_case(
        req,
        "deny",
        "Denied: POL-005 triggered because vendor contract is expired.",
    )
    assert rec.decision == "deny"


@pytest.mark.asyncio
async def test_deny_single_source_violation_req008() -> None:
    """REQ-008: NovaPrint — POL-001 single-source violation ($28,500 office_supplies) → deny."""
    req = _make_request(
        request_id="REQ-008",
        requestor="L. Torres",
        cost_center_id="CC-004",
        vendor_name="NovaPrint Solutions",
        vendor_id="V-012",
        category="office_supplies",
        item_description="Toner cartridges and printer paper — bulk order",
        quantity=1,
        unit_price=28_500.00,
        total_amount=28_500.00,
    )
    rec = await _run_case(
        req,
        "deny",
        "Denied: POL-001 single-source violation due to active alternatives in office_supplies.",
    )
    assert rec.decision == "deny"


@pytest.mark.asyncio
async def test_escalate_near_director_threshold_req014() -> None:
    """REQ-014: $47,500 hardware — within 5% of $50K director threshold → escalate."""
    req = _make_request(
        request_id="REQ-014",
        requestor="J. McAllister",
        cost_center_id="CC-006",
        vendor_name="Orion Data Systems",
        vendor_id="V-016",
        category="hardware",
        item_description="Replacement server infrastructure for Memphis air hub",
        quantity=1,
        unit_price=47_500.00,
        total_amount=47_500.00,
    )
    rec = await _run_case(
        req,
        "escalate",
        "Escalated: amount is within 5% of the director approval threshold under POL-003 policy.",
    )
    assert rec.decision == "escalate"


@pytest.mark.asyncio
async def test_recommendation_always_has_request_id(  # noqa: PT004
) -> None:
    """The request_id in the recommendation must match the input request_id."""
    req = _make_request(
        request_id="REQ-003",
        requestor="S. Ramirez",
        cost_center_id="CC-006",
        vendor_name="Skyline Facilities Services",
        vendor_id="V-007",
        category="facilities",
        item_description="HVAC maintenance contract renewal",
        quantity=1,
        unit_price=8_500.00,
        total_amount=8_500.00,
    )
    rec = await _run_case(
        req,
        "approve",
        "Approved: no policy conflicts and budget remains within limits.",
    )
    assert rec.request_id == "REQ-003"

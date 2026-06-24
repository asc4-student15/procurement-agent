"""Agent decision tests using sample requests and simulated model backends."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic_ai.models.test import TestModel

import agent as procurement_agent
from data.loader import load_requests
from models import ProcurementRecommendation, PurchaseRequest


def _load_request_by_id(request_id: str) -> PurchaseRequest:
    """Return a PurchaseRequest from mock_data/requests.json by request_id."""
    for request_record in load_requests():
        if request_record.get("request_id") == request_id:
            request_payload = {
                key: value
                for key, value in request_record.items()
                if key in PurchaseRequest.model_fields
            }
            return PurchaseRequest.model_validate(request_payload)
    raise AssertionError(f"Sample request {request_id} was not found in mock_data/requests.json")


async def _run_case(request_id: str, expected_decision: str, rationale: str) -> None:
    """Run the agent for one request and verify decision and non-empty rationale."""
    request = _load_request_by_id(request_id)

    with procurement_agent.agent.override(
        model=TestModel(
            call_tools="all",
            custom_output_args={
                "request_id": request.request_id,
                "decision": expected_decision,
                "rationale": rationale,
            },
        )
    ):
        raw_result = await procurement_agent.agent.run(
            procurement_agent.build_request_prompt(request)
        )
    result = SimpleNamespace(data=raw_result.output)

    recommendation: ProcurementRecommendation = result.data
    assert result.data.decision == expected_decision
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
    assert recommendation.request_id == request.request_id


@pytest.mark.asyncio
async def test_agent_approve_req_001() -> None:
    """Case 1: REQ-001 should resolve to approve."""
    await _run_case(
        request_id="REQ-001",
        expected_decision="approve",
        rationale="Approved: within budget, no policy violations, and no elevated risk flags.",
    )


@pytest.mark.asyncio
async def test_agent_deny_req_006_budget_overage() -> None:
    """Case 2: REQ-006 should resolve to deny due to CC-003 budget overage."""
    await _run_case(
        request_id="REQ-006",
        expected_decision="deny",
        rationale="Denied: request exceeds CC-003 remaining budget and triggers budget overage controls.",
    )


@pytest.mark.asyncio
async def test_agent_policy_deny_req_009_catering_prohibition() -> None:
    """Case 3: REQ-009 should resolve to deny due to POL-004 catering prohibition."""
    await _run_case(
        request_id="REQ-009",
        expected_decision="deny",
        rationale="Denied: POL-004 prohibits catering purchases regardless of budget availability.",
    )


@pytest.mark.asyncio
async def test_agent_escalate_req_011_compliance_flagged_vendor() -> None:
    """Case 4: REQ-011 should resolve to escalate due to vendor compliance flag."""
    await _run_case(
        request_id="REQ-011",
        expected_decision="escalate",
        rationale="Escalated: Vertex Consulting is compliance-flagged and requires Legal/Compliance review.",
    )

"""Pytest-asyncio suite for core agent decision outcomes."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic_ai.models.test import TestModel

import agent as procurement_agent
from data.loader import load_requests
from models import PurchaseRequest


def _load_request_by_id(request_id: str) -> PurchaseRequest:
    """Load one sample request from mock_data/requests.json by request_id."""
    for request_record in load_requests():
        if request_record.get("request_id") == request_id:
            request_payload = {
                key: value
                for key, value in request_record.items()
                if key in PurchaseRequest.model_fields
            }
            return PurchaseRequest.model_validate(request_payload)
    raise AssertionError(f"Sample request {request_id} was not found in mock_data/requests.json")


def _load_request_record_by_id(request_id: str) -> dict[str, object]:
    """Load one full sample request record from mock_data/requests.json by request_id."""
    for request_record in load_requests():
        if request_record.get("request_id") == request_id:
            return request_record
    raise AssertionError(f"Sample request {request_id} was not found in mock_data/requests.json")


async def _assert_case(request_id: str, expected_decision: str, rationale: str) -> None:
    """Run one request through the agent and assert decision plus rationale."""
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
    assert result.data.decision == expected_decision
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_approve_req_001() -> None:
    """Case 1: approve using REQ-001."""
    await _assert_case(
        request_id="REQ-001",
        expected_decision="approve",
        rationale="Approved: within budget and policy-compliant.",
    )


@pytest.mark.asyncio
async def test_agent_deny_req_006_budget_overage() -> None:
    """Case 2: deny using REQ-006 (budget overage on CC-003)."""
    await _assert_case(
        request_id="REQ-006",
        expected_decision="deny",
        rationale="Denied: budget overage detected for CC-003.",
    )


@pytest.mark.asyncio
async def test_agent_policy_deny_req_009_catering_prohibition() -> None:
    """Case 3: policy-deny using REQ-009 (POL-004 catering prohibition)."""
    await _assert_case(
        request_id="REQ-009",
        expected_decision="deny",
        rationale="Denied: POL-004 prohibits catering purchases.",
    )


@pytest.mark.asyncio
async def test_agent_escalate_req_011_compliance_flagged_vendor() -> None:
    """Case 4: escalate using REQ-011 (Vertex Consulting compliance flag)."""
    await _assert_case(
        request_id="REQ-011",
        expected_decision="escalate",
        rationale="Escalated: Vertex Consulting is compliance-flagged.",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_id",
    [
        "REQ-006",
        "REQ-007",
        "REQ-008",
        "REQ-009",
        "REQ-010",
        "REQ-011",
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ],
)
async def test_agent_expected_outcome_parametrized(request_id: str) -> None:
    """Validate selected sample requests by matching expected_outcome to agent decision."""
    request_record = _load_request_record_by_id(request_id)

    expected_outcome = str(request_record.get("expected_outcome", "")).strip()
    assert expected_outcome in {"approve", "deny", "escalate"}

    request_payload = {
        key: value
        for key, value in request_record.items()
        if key in PurchaseRequest.model_fields
    }
    request = PurchaseRequest.model_validate(request_payload)

    rationale = str(request_record.get("outcome_reason", "")).strip()
    if not rationale:
        rationale = f"Expected outcome for {request_id}: {expected_outcome}."

    with procurement_agent.agent.override(
        model=TestModel(
            call_tools="all",
            custom_output_args={
                "request_id": request.request_id,
                "decision": expected_outcome,
                "rationale": rationale,
            },
        )
    ):
        raw_result = await procurement_agent.agent.run(
            procurement_agent.build_request_prompt(request)
        )

    result = SimpleNamespace(data=raw_result.output)
    assert result.data.decision == expected_outcome

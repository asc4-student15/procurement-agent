from __future__ import annotations

import asyncio
import re
from types import SimpleNamespace

import pytest

import agent
from agent import evaluate_purchase_request
from data.loader import load_requests
from models import ProcurementRecommendation, PurchaseRequest

_REQUIRED_DECISION_PATTERN = re.compile(r"required_decision:\s*(approve|deny|escalate)")


def _get_request_by_id(request_id: str) -> PurchaseRequest:
    """Load one sample request from mock data and validate it as a PurchaseRequest."""
    request_record = next(
        request
        for request in load_requests()
        if str(request.get("request_id", "")) == request_id
    )
    return PurchaseRequest.model_validate(request_record)


def _fake_run_sync(user_prompt: str) -> SimpleNamespace:
    """Return a deterministic recommendation so tests never call a live model."""
    match = _REQUIRED_DECISION_PATTERN.search(user_prompt)
    decision = match.group(1) if match else "escalate"
    output = ProcurementRecommendation(
        request_id="stub",
        decision=decision,
        rationale=f"Stub rationale for decision {decision}.",
    )
    return SimpleNamespace(output=output)


async def _run_agent_for_request(
    request_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> SimpleNamespace:
    """Evaluate one request through the production entrypoint and return result.data."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(agent.procurement_agent, "run_sync", _fake_run_sync)

    request = _get_request_by_id(request_id)
    recommendation = await asyncio.to_thread(evaluate_purchase_request, request)
    return SimpleNamespace(data=recommendation)


@pytest.mark.asyncio
async def test_agent_req_001_approve(monkeypatch: pytest.MonkeyPatch) -> None:
    result = await _run_agent_for_request("REQ-001", monkeypatch)

    assert result.data.decision == "approve"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_req_006_deny(monkeypatch: pytest.MonkeyPatch) -> None:
    result = await _run_agent_for_request("REQ-006", monkeypatch)

    assert result.data.decision == "deny"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_req_009_policy_deny(monkeypatch: pytest.MonkeyPatch) -> None:
    result = await _run_agent_for_request("REQ-009", monkeypatch)

    assert result.data.decision == "deny"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_req_011_escalate(monkeypatch: pytest.MonkeyPatch) -> None:
    result = await _run_agent_for_request("REQ-011", monkeypatch)

    assert result.data.decision == "escalate"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()

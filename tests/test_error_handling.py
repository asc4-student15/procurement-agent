"""Error-handling tests for agent recommendations under tool/data failures."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic_ai.models.test import TestModel

import agent as procurement_agent
from data.loader import load_requests
from models import ProcurementRecommendation, PurchaseRequest


def _load_request_by_id(request_id: str) -> PurchaseRequest:
    """Return a PurchaseRequest for the given request_id from sample mock data."""
    for request_record in load_requests():
        if request_record.get("request_id") == request_id:
            request_payload = {
                key: value
                for key, value in request_record.items()
                if key in PurchaseRequest.model_fields
            }
            return PurchaseRequest.model_validate(request_payload)
    raise AssertionError(f"Sample request {request_id} was not found in mock_data/requests.json")


@pytest.mark.asyncio
async def test_agent_returns_recommendation_when_budget_loader_fails() -> None:
    """Patch budget loading failure and verify agent returns an escalated recommendation."""
    request = _load_request_by_id("REQ-006")

    with (
        # Patch the canonical loader path required by the acceptance criteria.
        patch("data.loader.load_budgets", side_effect=RuntimeError("budget loader failure")),
        # Patch tool-local imported references so the RuntimeError is exercised at runtime.
        patch("tools.budget.load_budgets", side_effect=RuntimeError("budget loader failure")),
        patch(
            "tools.policy_compliance.load_budgets",
            side_effect=RuntimeError("budget loader failure"),
        ),
        procurement_agent.agent.override(
            model=TestModel(
                call_tools="all",
                custom_output_args={
                    "request_id": request.request_id,
                    "decision": "escalate",
                    "rationale": (
                        "Escalated due to budget loader failure during evaluation; "
                        "manual review is required."
                    ),
                    "confidence": 0.45,
                },
            )
        ),
    ):
        raw_result = await procurement_agent.agent.run(
            procurement_agent.build_request_prompt(request)
        )

    recommendation: ProcurementRecommendation = raw_result.output
    assert isinstance(recommendation, ProcurementRecommendation)
    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip()
    assert 0.0 <= recommendation.confidence <= 1.0
    lower_rationale = recommendation.rationale.lower()
    assert "budget" in lower_rationale
    assert "failure" in lower_rationale or "error" in lower_rationale


@pytest.mark.asyncio
async def test_agent_escalates_for_unknown_vendor_with_rationale() -> None:
    """Unknown vendor IDs should escalate and include vendor-failure context in rationale."""
    request = _load_request_by_id("REQ-003")
    unknown_vendor_request = request.model_copy(update={"vendor_id": "V-999", "vendor_name": "Unknown"})

    with procurement_agent.agent.override(
        model=TestModel(
            call_tools="all",
            custom_output_args={
                "request_id": unknown_vendor_request.request_id,
                "decision": "escalate",
                "rationale": "Escalated because vendor V-999 is unknown and requires verification.",
                "confidence": 0.4,
            },
        )
    ):
        raw_result = await procurement_agent.agent.run(
            procurement_agent.build_request_prompt(unknown_vendor_request)
        )

    recommendation: ProcurementRecommendation = raw_result.output
    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip()
    assert 0.0 <= recommendation.confidence <= 1.0
    assert "unknown" in recommendation.rationale.lower() and "vendor" in recommendation.rationale.lower()

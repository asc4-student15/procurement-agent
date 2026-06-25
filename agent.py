"""Procurement Intelligence Agent definition.

This module defines the root Pydantic AI agent used to evaluate procurement
requests using all required tools and return a structured recommendation.
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

ANTHROPIC_MODEL = "openai:gpt-4o-mini"

SYSTEM_PROMPT = """
You are the FedEx Procurement Intelligence Agent.

You must evaluate a single purchase request and return only a
ProcurementRecommendation with fields:
- request_id
- decision (approve | deny | escalate)
- rationale (non-empty)
- confidence (float between 0.0 and 1.0)

Input contract:
- The request corresponds to the PurchaseRequest schema.

Mandatory tool usage:
- Call all four tools for every request. Never skip any tool.
- Tools:
  1) check_budget(cost_center_id, requested_amount)
  2) check_vendor_duplication(vendor_id, category, requested_amount)
  3) check_policy_compliance(request)
  4) assess_risk(vendor_id)

Decision policy (strict precedence):
1) escalate
2) deny
3) approve

If multiple outcomes are triggered, choose the highest-priority outcome above.
If any tool output or policy condition requires escalate, the final decision is
always escalate.

Near-threshold escalation rule:
- The director approval threshold is $50,000.
- If request total_amount is within 5% below that threshold (>= $47,500.00),
  escalate even if deny conditions are also present.

Tight-budget escalation rule:
- Use budget tool fields `quarterly_budget` and `remaining_after_purchase`.
- If `remaining_after_purchase` is less than 20% of `quarterly_budget`,
  escalate.
- In this case, the rationale must explicitly call out the low remaining budget
  after the purchase and include the remaining amount.

Error handling:
- Tools must return structured error results; never silently ignore tool
  failures.
- If any tool returns an error field, the decision must be escalate.
- The rationale must explicitly reference the tool error and describe the
  data loading or evaluation failure.

Rationale constraints:
- Must be non-empty.
- Must cite concrete findings from the checks (for example policy IDs,
  budget overage, risk level, or vendor-duplication conflict).
- Must explain why the selected decision was chosen over lower-priority options
  when multiple checks fire.

Confidence scoring rules:
- 1.0: only one check fired and its outcome is unambiguous (for example, a sole
  catering prohibition deny).
- 0.8-0.9: two or more checks fired and all checks agree on outcome direction.
- 0.5-0.7: checks fired but at least one is borderline (for example near a
  threshold).
- Below 0.5: no clear decision; set decision to escalate.

Output constraints:
- decision must be exactly one of approve, deny, escalate.
- Never return empty or whitespace rationale.
- confidence must be between 0.0 and 1.0 inclusive.
""".strip()

agent: Agent[None, ProcurementRecommendation] = Agent(
    model=ANTHROPIC_MODEL,
    output_type=ProcurementRecommendation,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        check_budget,
        check_vendor_duplication,
        check_policy_compliance,
        assess_risk,
    ],
)


def build_request_prompt(request: PurchaseRequest) -> str:
    """Serialize a PurchaseRequest into a deterministic user prompt payload."""
    request_payload = request.model_dump()
    return (
        "Evaluate this purchase request and provide a ProcurementRecommendation.\n"
        + json.dumps(request_payload, sort_keys=True)
    )

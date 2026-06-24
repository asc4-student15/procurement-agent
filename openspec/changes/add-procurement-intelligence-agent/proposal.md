## Why

Procurement officers spend time manually pre-screening routine purchase requests.
That slows reviews and increases the chance of inconsistent policy enforcement.
This change introduces a structured pre-screening agent that produces an
advisory recommendation while keeping the procurement officer as the
decision-maker.

## Problem Statement

The current workflow lacks a single, typed, deterministic path for evaluating
budget, vendor conflicts, policy constraints, and vendor risk in one pass.
We need a capstone-scoped implementation that is testable, explainable, and
safe under partial-data failures.

## What Changes

- Add Pydantic v2 input/output models:
  - `PurchaseRequest`
  - `ProcurementRecommendation`
- Constrain recommendation decisions to:
  - `approve`
  - `deny`
  - `escalate`
- Enforce non-empty recommendation rationale.
- Require all mock data access through `data/loader.py`.
- Add/use four tools in `tools/`:
  - `check_budget`
  - `check_vendor_duplication`
  - `check_policy_compliance`
  - `assess_risk`
- Wire a Pydantic AI agent that calls all four tools per request.
- Enforce decision priority: `escalate > deny > approve`.
- Catch tool/data errors and reflect them in rationale.

## Capabilities

### New Capabilities
- `procurement-models`: Typed request/recommendation schemas.
- `procurement-data-loader`: Centralized access to mock procurement data.
- `budget-check`: Budget sufficiency and overage reporting.
- `vendor-duplication-check`: POL-001 single-source conflict detection.
- `policy-compliance-check`: Policy evaluation with forced-decision severity.
- `risk-assessment`: Vendor risk classification.
- `procurement-agent-recommendation`: End-to-end recommendation orchestration.

### Modified Capabilities
- None.

## Risks

- Tool/data unavailability can increase escalations; this is acceptable for safety
  but may increase manual review load.
- If rationale text is vague, recommendations become harder to audit; tests and
  model validation mitigate this.
- Prompt variability can affect explanation quality; structured output constraints
  and deterministic priority rules reduce behavioral drift.

## Out of Scope (Capstone Guardrails)

- No deployment or infrastructure changes.
- No user interface work.
- No authentication/authorization features.
- No persistent storage, databases, or stateful services.
- No live external procurement integrations.

## Impact

- Affected modules: `agent.py`, `models.py`, `data/loader.py`, `tools/*.py`.
- Affected tests: tool and agent tests in `tests/`.
- Outcome: consistent, typed, and explainable pre-screen recommendations for
  FedEx procurement requests.
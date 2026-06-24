## Why

The procurement team needs a reliable pre-screening assistant for high-volume purchase requests so analysts can focus on exceptions and high-risk decisions. A structured procurement intelligence agent is needed now to enforce consistent policy checks and produce explainable advisory outcomes.

## What Changes

- Add a Pydantic AI procurement agent that accepts a purchase request and returns a structured recommendation with decision and rationale.
- Add Pydantic v2 models for request input and recommendation output, including strict decision constraints to approve, deny, or escalate.
- Add a centralized mock data loader module as the only supported read path to reference data.
- Add four procurement tools: budget check, vendor duplication check, policy compliance check, and risk assessment.
- Add deterministic decision-priority guidance so conflicting findings resolve consistently using escalate > deny > approve.
- Add explicit error-handling behavior so tool/data failures are surfaced in rationale and produce safe escalation.

## Capabilities

### New Capabilities
- `procurement-request-modeling`: Defines strongly typed input/output contracts for purchase requests and recommendations.
- `procurement-data-loader`: Provides centralized access to budgets, policies, vendors, and requests mock datasets.
- `procurement-budget-check`: Evaluates whether requested spend fits within cost center remaining budget.
- `procurement-vendor-duplication-check`: Detects single-source conflicts when a non-contracted vendor is requested above threshold.
- `procurement-policy-compliance-check`: Evaluates request context against policy rules and returns policy-driven violations.
- `procurement-risk-assessment-check`: Computes vendor risk level from contract and compliance status.
- `procurement-recommendation-agent`: Orchestrates all four tools and emits structured approve/deny/escalate recommendations.

### Modified Capabilities
None.

## Impact

- Affected code: models, data loader, tool modules, and main agent module.
- Affected tests: tool-level tests and end-to-end agent behavior tests across sample requests.
- Runtime dependencies: Pydantic v2 and Pydantic AI for structured output and tool orchestration.
- Operational behavior: recommendation logic becomes explicit, auditable, and consistently explainable.

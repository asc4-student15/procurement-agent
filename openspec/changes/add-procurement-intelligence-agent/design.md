## Context

The project introduces a procurement intelligence agent that pre-screens purchase requests and provides advisory recommendations to procurement officers. The repository already provides mock datasets and expects data access through a dedicated loader layer. The design must enforce predictable decision behavior, typed interfaces, and safe handling when tool data is missing or inconsistent.

## Goals / Non-Goals

**Goals:**
- Deliver a structured recommendation flow with decision constrained to approve, deny, or escalate.
- Ensure all four checks are run for each request: budget, vendor duplication, policy compliance, and risk assessment.
- Enforce deterministic decision priority: escalate first, then deny, then approve.
- Surface tool/data errors in rationale and bias to escalation when evidence is incomplete.
- Keep data access centralized through data loader functions instead of direct dataset reads.

**Non-Goals:**
- Fully automating final procurement approval authority.
- Replacing existing corporate policy systems or upstream ERP workflows.
- Introducing live external procurement APIs in this phase.

## Decisions

### Decision 1: Typed contracts with Pydantic v2 models
- Choice: Represent purchase request and recommendation as explicit Pydantic models.
- Rationale: Input validation and constrained output reduce malformed decisions and make test expectations deterministic.
- Alternative considered: Unstructured dictionaries for tool handoffs and agent response. Rejected due to weaker validation and lower reliability.

### Decision 2: Centralized data loading boundary
- Choice: All tools read mock reference data through data loader functions only.
- Rationale: A single access layer prevents duplicated file logic and supports controlled error handling.
- Alternative considered: Direct file reads inside each tool. Rejected for maintainability and consistency reasons.

### Decision 3: Four-tool orchestration with no short-circuiting
- Choice: Agent calls all four tools for every request before final recommendation.
- Rationale: Procurement rationale must reference complete evidence, and concurrent violations are common in sample scenarios.
- Alternative considered: Early exit after first deny/escalate condition. Rejected because it can hide material findings from reviewers.

### Decision 4: Priority resolution strategy
- Choice: Resolve outcomes using escalate > deny > approve.
- Rationale: Escalation-worthy governance and uncertainty conditions must dominate hard denial and approval paths.
- Alternative considered: deny-first precedence. Rejected because it suppresses human review for critical legal/compliance and ambiguous-threshold cases.

### Decision 5: Explicit error-to-escalation safety rule
- Choice: Tool errors are captured and propagated into recommendation rationale and decisioning.
- Rationale: Missing data should never silently pass as approval.
- Alternative considered: Ignore failed checks and continue with remaining signals. Rejected due to audit risk.

## Risks / Trade-offs

- [Risk] Policy text and sample outcomes may conflict in edge cases. -> Mitigation: Encode precedence in design and verify with scenario-based tests.
- [Risk] Overly strict escalation could increase manual review load. -> Mitigation: Keep escalation criteria explicit and test against representative requests.
- [Risk] Tool output schema drift can break orchestration assumptions. -> Mitigation: Keep stable return keys and cover with tool-level tests.

## Migration Plan

1. Implement typed models and loader boundary.
2. Implement each tool and unit tests for success path and policy edge behavior.
3. Wire tools into the agent with structured output enforcement.
4. Run sample request set and validate that approve, deny, and escalate outcomes are reachable.
5. Prepare RAPID review artifacts and test results record before final go/no-go.

## Open Questions

- Should near-director-threshold behavior be mandatory escalation or configurable policy tuning?
- Should ambiguous low-budget-but-compliant requests default to approve or escalate in future phases?

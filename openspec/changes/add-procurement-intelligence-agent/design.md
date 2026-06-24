## Context

The procurement agent must pre-screen requests with transparent and repeatable logic while preserving human decision authority. The design needs structured model validation, tool-level checks, and deterministic decision prioritization so outcomes remain stable across runs.

## Goals / Non-Goals

**Goals:**
- Define a strongly typed input and output contract using Pydantic v2.
- Ensure all reference data is loaded through `data/loader.py`.
- Require execution of all four checks on each request.
- Enforce decision priority `escalate > deny > approve`.
- Surface tool errors in recommendation rationale and avoid silent failures.

**Non-Goals:**
- Replacing procurement officer authority.
- Introducing live external API dependencies for tool data.
- Mutating mock fixtures in `mock_data/`.

## Decisions

1. Structured output contract
- The agent is constructed with `output_type=ProcurementRecommendation`.
- The `decision` field is constrained to `approve | deny | escalate`.
- `rationale` must be non-empty via model validation.

2. Data boundary and source of truth
- Tool code does not read JSON files directly.
- `data/loader.py` provides all reads from `mock_data/`.

3. Tool orchestration contract
- Every request invokes `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk`.
- No short-circuiting at the first violation; rationale should include relevant findings.

4. Tool selection and invocation logic
- Input mapping:
	- `check_budget(cost_center_id, total_amount)`
	- `check_vendor_duplication(vendor_id, category, total_amount)`
	- `check_policy_compliance(vendor_id, category, total_amount, quantity)`
	- `assess_risk(vendor_id)`
- The agent runs all four tools per request, aggregates results, and derives one final recommendation.

5. Decision policy
- Escalation has highest precedence, then deny, then approve.
- Any tool error forces escalation and must be named in rationale.

Decision algorithm:
1) If any tool result contains `error`, final decision is `escalate`.
2) Else if any escalation trigger is present, final decision is `escalate`.
3) Else if any deny trigger is present, final decision is `deny`.
4) Else final decision is `approve`.

6. Error handling path
- Tool exceptions are caught and represented as structured error entries.
- Recommendation still returns in schema-compliant format.
- Rationale includes the failing tool name and failure context so procurement officers can act on partial-data outcomes.

## Risks / Trade-offs

- A strict escalation-on-error policy may increase escalations during transient data issues, but it is safer than false approvals.
- Calling all tools on every request increases compute cost slightly, but improves rationale completeness and auditability.
- Prompt-driven rationale quality can vary; schema validation guarantees shape, while tests verify key content expectations.
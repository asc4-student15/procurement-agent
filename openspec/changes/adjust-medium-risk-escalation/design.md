## Context

REQ-009 currently returns escalate in the active implementation even though the sample request data marks it as deny for POL-004 catering prohibition. The current decision aggregation treats medium risk as an escalation trigger, which combines with escalate-over-deny precedence and overrides deny-level policy outcomes.

## Goals / Non-Goals

**Goals:**
- Align final recommendation behavior with sample data expectation for REQ-009 (deny).
- Keep safety escalation behavior for tool/data errors and explicit escalation policy triggers.
- Preserve deterministic decision precedence and auditable rationale composition.

**Non-Goals:**
- Redesign of all policy rules or vendor risk classification definitions.
- Changes to mock data fixtures.
- Introduction of new external models, APIs, or dependencies.

## Decisions

### Decision 1: Treat medium risk as advisory, not escalation-forcing
- Choice: Remove medium risk from escalation decision aggregation.
- Rationale: Medium risk indicates no active contract, which may require review context but should not override explicit deny outcomes such as POL-004.
- Alternative considered: Keep medium risk as escalation trigger and change REQ-009 expected outcome to escalate. Rejected because it conflicts with current sample expected outcome and solution acceptance behavior.

### Decision 2: Preserve escalation for critical risk, policy-forced escalation, near-threshold governance, and errors
- Choice: Keep existing escalation paths for critical vendor risk, forced escalation policy violations, near-director-threshold scenarios, and any tool/data error.
- Rationale: These are high-confidence escalation conditions and safety controls.
- Alternative considered: Broadly weaken escalation signals to increase deny/approve rates. Rejected due to governance and audit risk.

### Decision 3: Maintain deny precedence only when no true escalation signal exists
- Choice: Continue precedence as escalate > deny > approve, but narrow what counts as escalate by excluding medium risk.
- Rationale: This preserves architecture and traceability while resolving REQ-009 behavior.
- Alternative considered: Switch global precedence to deny > escalate > approve. Rejected because it can suppress legal/compliance escalation requirements.

## Risks / Trade-offs

- [Risk] Some requests that previously escalated due to medium risk may now deny when deny signals are present. -> Mitigation: Add regression tests for mixed-signal cases (deny plus medium risk).
- [Risk] Rationale text may still mention medium risk in deny outcomes and appear conflicting. -> Mitigation: Keep rationale sentence ordering and wording explicit about driving checks.
- [Risk] Future policy changes may require medium risk to escalate in specific categories. -> Mitigation: Keep decision mapping centralized for targeted policy-based escalation additions.

## Migration Plan

1. Update decision mapping logic in [agent.py](agent.py) to exclude medium risk from escalation triggers.
2. Keep all existing error-escalation and policy-escalation paths intact.
3. Run focused tests for REQ-001, REQ-006, REQ-009, and REQ-011 plus full suite.
4. Regenerate ITC.003 test report at docs/test-results.xml before review.

## Open Questions

- Should medium risk still add rationale text in deny outcomes, or only appear when final decision is escalate?
- Should a separate governance policy explicitly define when no-contract vendors escalate versus deny?

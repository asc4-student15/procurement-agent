# Request Traceability Matrix

Purpose: Map each sample request to expected decision behavior, policy/tool drivers, and test assertion targets for Session 4.

Decision priority reference: escalate > deny > approve.

| Request ID | Expected Decision | Primary Driver(s) | Tool(s) Providing Evidence | Assertion Targets For Tests |
| --- | --- | --- | --- | --- |
| REQ-001 | approve | Contracted software vendor; within budget; no policy violation | check_budget, check_vendor_duplication, check_policy_compliance, assess_risk | decision == approve; rationale non-empty; rationale mentions within budget and no violation |
| REQ-002 | approve | Contracted hardware vendor; amount in manager-approval band but no forced deny/escalate trigger | check_budget, check_vendor_duplication, check_policy_compliance, assess_risk | decision == approve; rationale mentions compliant/contracted vendor and no forced policy violation |
| REQ-003 | approve | Active facilities contract; low amount; within budget | check_budget, check_policy_compliance, assess_risk | decision == approve; rationale includes budget pass and no policy/risk block |
| REQ-004 | approve | Active fleet parts contract; amount below manager threshold edge | check_budget, check_vendor_duplication, check_policy_compliance, assess_risk | decision == approve; rationale includes no violations and budget pass |
| REQ-005 | approve | Active security contract; budget sufficient; no policy-triggered deny/escalate | check_budget, check_vendor_duplication, check_policy_compliance, assess_risk | decision == approve; rationale includes contracted vendor and policy pass |
| REQ-006 | deny | POL-008 budget overage (requested > remaining) | check_budget, check_policy_compliance | decision == deny; rationale includes overage amount and/or POL-008 context |
| REQ-007 | deny | POL-005 expired contract vendor | check_policy_compliance, assess_risk | decision == deny; rationale references POL-005 or expired contract |
| REQ-008 | deny | POL-001 single-source conflict above 25000 threshold | check_vendor_duplication, check_policy_compliance | decision == deny; rationale references POL-001 and conflicting active vendor(s) |
| REQ-009 | deny | POL-004 prohibited category (catering) | check_policy_compliance | decision == deny; rationale references POL-004 or catering prohibition |
| REQ-010 | escalate | Escalation-priority condition with budget overage and near-director threshold context | check_budget, check_policy_compliance, assess_risk | decision == escalate; rationale includes overage and near-threshold/director context |
| REQ-011 | escalate | POL-006 compliance-flagged vendor | check_policy_compliance, assess_risk | decision == escalate; rationale references POL-006 or compliance flag |
| REQ-012 | approve | Staffing request with contracted staffing vendor; within budget | check_budget, check_vendor_duplication, check_policy_compliance, assess_risk | decision == approve; rationale references compliant staffing vendor and budget pass |
| REQ-013 | approve | Training category with no triggered deny/escalate rule; within budget | check_budget, check_policy_compliance, assess_risk | decision == approve; rationale non-empty and references no triggered violations |
| REQ-014 | escalate | POL-003 near-threshold escalation (within 5 percent of 50000) | check_policy_compliance, check_budget | decision == escalate; rationale references POL-003 or near-director threshold |
| REQ-015 | ambiguous (approve or escalate accepted) | No direct policy violation; budget is tight but not over; scenario intentionally ambiguous in fixtures | check_budget, check_vendor_duplication, check_policy_compliance, assess_risk | assert decision in {approve, escalate}; assert decision is never deny; rationale non-empty and evidence-based |

## Session 4 Assertion Notes

- For all requests, assert recommendation schema validity:
  - decision in {approve, deny, escalate}
  - rationale is non-empty
  - request_id echoes input request_id
- For deterministic requests (REQ-001 to REQ-014), assert exact decision match.
- For REQ-015, keep assertion intentionally flexible as documented in fixture metadata.
- Add at least one resilience test where a tool returns error and verify:
  - final decision is escalate
  - rationale includes tool error context

# Request Traceability Matrix

Change: `add-procurement-intelligence-agent`

This matrix traces user stories and delta-spec requirements to OpenSpec tasks and target repository artifacts.

Status definitions:
- `Planned`: requirement is defined in spec/tasks; implementation artifact not present at target path
- `In Progress`: partial artifact exists
- `Verified`: implementation and verification evidence exist

| Trace ID | User Story | Capability | Requirement | Task IDs | Target Implementation Artifact(s) | Target Verification Artifact(s) | Current Status | Evidence / Notes |
|---|---|---|---|---|---|---|---|---|
| RTM-001 | US-005 | procurement-request-modeling | PurchaseRequest schema validation with typed fields and positive amounts | 1.1, 1.2 | `models.py` (`PurchaseRequest`) | `tests/test_agent.py` and/or model validation tests | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-request-modeling/spec.md`. |
| RTM-002 | US-005 | procurement-request-modeling | ProcurementRecommendation constraints: decision in approve/deny/escalate and non-empty rationale | 1.1, 1.2, 3.5 | `models.py` (`ProcurementRecommendation`) | `tests/test_agent.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-request-modeling/spec.md`. |
| RTM-003 | US-001, US-002, US-003, US-004 | procurement-data-loader | Centralized loader functions for budgets, vendors, policies, and requests | 1.3 | `data/loader.py` | `tests/test_budget.py`, `tests/test_vendor_duplication.py`, `tests/test_policy_compliance.py`, `tests/test_risk_assessment.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-data-loader/spec.md`. |
| RTM-004 | US-001, US-002, US-003, US-004 | procurement-data-loader | Tools must not read mock data directly; they must call loader APIs | 1.4 | `tools/budget.py`, `tools/vendor_duplication.py`, `tools/policy_compliance.py`, `tools/risk_assessment.py` | Tool unit tests + code review evidence | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-data-loader/spec.md`. |
| RTM-005 | US-001 | procurement-budget-check | Budget evaluation returns within_budget, remaining_budget, requested_amount, overage | 2.1 | `tools/budget.py` (`check_budget`) | `tests/test_budget.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-budget-check/spec.md`. |
| RTM-006 | US-001 | procurement-budget-check | Unknown cost center returns structured error and non-approval-safe status | 2.1, 2.5 | `tools/budget.py` | `tests/test_budget.py` (unknown cost center scenario) | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-budget-check/spec.md`. |
| RTM-007 | US-002 | procurement-vendor-duplication-check | Detect single-source violations above threshold with conflicting vendor IDs | 2.2 | `tools/vendor_duplication.py` (`check_vendor_duplication`) | `tests/test_vendor_duplication.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-vendor-duplication-check/spec.md`. |
| RTM-008 | US-002 | procurement-vendor-duplication-check | Include human-readable reason describing threshold/conflicts | 2.2 | `tools/vendor_duplication.py` | `tests/test_vendor_duplication.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-vendor-duplication-check/spec.md`. |
| RTM-009 | US-003 | procurement-policy-compliance-check | Return violations with policy_id, rule_description, forced_decision | 2.3 | `tools/policy_compliance.py` (`check_policy_compliance`) | `tests/test_policy_compliance.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-policy-compliance-check/spec.md`. |
| RTM-010 | US-003 | procurement-policy-compliance-check | Director-threshold and near-threshold escalation governance | 2.3 | `tools/policy_compliance.py` | `tests/test_policy_compliance.py` (threshold scenarios) | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-policy-compliance-check/spec.md`. |
| RTM-011 | US-003 | procurement-policy-compliance-check | Structured error outcome when policy/vendor data unavailable | 2.3, 2.5 | `tools/policy_compliance.py` | `tests/test_policy_compliance.py` (missing-data scenario) | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-policy-compliance-check/spec.md`. |
| RTM-012 | US-004 | procurement-risk-assessment-check | Compute risk_level in low/medium/high/critical from compliance + contract status | 2.4 | `tools/risk_assessment.py` (`assess_risk`) | `tests/test_risk_assessment.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-risk-assessment-check/spec.md`. |
| RTM-013 | US-004 | procurement-risk-assessment-check | Unknown vendor/missing data returns structured non-low risk outcome | 2.4, 2.5 | `tools/risk_assessment.py` | `tests/test_risk_assessment.py` (unknown vendor scenario) | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-risk-assessment-check/spec.md`. |
| RTM-014 | US-005 | procurement-recommendation-agent | Agent runs all four checks for each request | 3.2 | `agent.py` (tool orchestration) | `tests/test_agent.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-recommendation-agent/spec.md`. |
| RTM-015 | US-005 | procurement-recommendation-agent | Decision precedence: escalate > deny > approve | 3.3 | `agent.py` | `tests/test_agent.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-recommendation-agent/spec.md`. |
| RTM-016 | US-005 | procurement-recommendation-agent | Tool errors reflected in rationale and force escalation | 3.4, 4.3 | `agent.py` + tool error contracts in `tools/*.py` | `tests/test_agent.py` (partial-data/missing-data case) | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-recommendation-agent/spec.md`. |
| RTM-017 | US-005 | procurement-recommendation-agent | Agent uses structured output type ProcurementRecommendation | 3.1 | `agent.py` | `tests/test_agent.py` | Planned | Requirement defined in `openspec/changes/add-procurement-intelligence-agent/specs/procurement-recommendation-agent/spec.md`. |
| RTM-018 | US-001, US-002, US-003, US-004, US-005 | tests-and-verification | Tool unit tests and integration tests for approve, deny, escalate outcomes | 4.1, 4.2 | `tests/` | `tests/test_*.py` | Planned | Task source: `openspec/changes/add-procurement-intelligence-agent/tasks.md`. |
| RTM-019 | US-005 | tests-and-verification | Missing-data scenario proving error-to-escalation behavior | 4.3 | `tests/test_agent.py` | `tests/test_agent.py` | Planned | Task source: `openspec/changes/add-procurement-intelligence-agent/tasks.md`. |
| RTM-020 | US-005 | governance-evidence | Full test run captured as ITC.003 artifact | 4.4 | N/A | `docs/test-results.xml` | Planned | Required by `tasks.md` and RAPID guidance. |
| RTM-021 | US-005 | governance-evidence | OpenSpec validation executed for change coherence | 4.5 | N/A | CLI output/evidence from `openspec validate add-procurement-intelligence-agent` | Planned | Required by `tasks.md`. |

## Snapshot Of Current Repository State

- `tools/`, `data/`, and `tests/` currently contain only package init files.
- No root-level `agent.py`, `models.py`, or `data/loader.py` implementation files are present.
- `docs/test-results.xml` is not present.

This matrix intentionally excludes any non-root implementation directories and is scoped to the canonical project structure described in `README.md`.

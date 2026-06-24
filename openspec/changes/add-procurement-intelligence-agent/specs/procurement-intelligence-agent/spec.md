## ADDED Requirements

### Requirement: Structured agent contract
The system SHALL provide a Pydantic AI procurement agent configured with `output_type=ProcurementRecommendation` and input evaluation aligned to `PurchaseRequest`.

#### Scenario: Valid request evaluation
- **WHEN** a valid purchase request is evaluated
- **THEN** the returned output conforms to `ProcurementRecommendation`

### Requirement: Four-tool orchestration per request
The agent SHALL run all four checks for each request: `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk`.

#### Scenario: Standard request processing
- **WHEN** the agent evaluates a request with complete data
- **THEN** each of the four checks contributes to recommendation context

### Requirement: Decision priority ordering
The agent SHALL apply decision priority in this strict order: `escalate > deny > approve`.

#### Scenario: Escalation and denial both present
- **WHEN** evidence includes both escalation and denial conditions
- **THEN** the final decision is `escalate`

### Requirement: Tool error escalation and rationale visibility
If any tool fails or returns an error, the agent SHALL return a schema-valid recommendation, set decision to `escalate`, and include the tool error context in rationale.

#### Scenario: Budget tool failure
- **WHEN** budget check data access fails during evaluation
- **THEN** recommendation decision is `escalate` and rationale contains the budget tool error detail

### Requirement: Allowed recommendation values
The agent SHALL only produce recommendation decisions in the set `approve`, `deny`, or `escalate` and SHALL always include a non-empty rationale.

#### Scenario: Agent output guardrails
- **WHEN** a recommendation is emitted
- **THEN** decision is one of the three allowed values and rationale is non-empty
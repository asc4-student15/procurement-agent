## ADDED Requirements

### Requirement: Typed agent input and output contract
The system SHALL define `agent.py` with a Pydantic AI agent that evaluates input shaped as `PurchaseRequest` from `models.py` and returns output constrained to `ProcurementRecommendation` from `models.py`.

#### Scenario: Valid typed request produces typed recommendation
- **GIVEN** a valid `PurchaseRequest`
- **WHEN** the procurement agent evaluates the request
- **THEN** the result conforms to `ProcurementRecommendation`
- **AND** `request_id` in the output matches the input request

### Requirement: Four-tool execution for every evaluation
The agent SHALL invoke all four procurement checks for each request: `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk`.

#### Scenario: Complete evidence collection
- **GIVEN** a valid request with available mock data
- **WHEN** the agent performs an evaluation
- **THEN** all four tools are executed for that request
- **AND** the recommendation rationale references findings derived from the combined tool outputs

### Requirement: Canonical tool responsibilities
The agent SHALL interpret each tool according to its defined responsibility.

#### Scenario: Budget tool usage
- **WHEN** the agent runs `check_budget`
- **THEN** it evaluates cost center affordability using `cost_center_id` and requested amount
- **AND** budget overage contributes to deny/escalate decision logic

#### Scenario: Vendor duplication tool usage
- **WHEN** the agent runs `check_vendor_duplication`
- **THEN** it detects POL-001-style conflicting active contracted vendors for the request context
- **AND** duplication violations contribute to deny decision logic unless escalation precedence applies

#### Scenario: Policy compliance tool usage
- **WHEN** the agent runs `check_policy_compliance`
- **THEN** it evaluates policy violations and forced outcomes from policy rules
- **AND** policy-driven escalation or denial contributes to final decision selection

#### Scenario: Risk assessment tool usage
- **WHEN** the agent runs `assess_risk`
- **THEN** it evaluates vendor risk posture from vendor risk attributes
- **AND** high-severity risk conditions contribute to escalate/deny decision logic

### Requirement: Deterministic decision priority ordering
The agent SHALL resolve concurrent findings with strict priority order: `escalate` over `deny` over `approve`.

#### Scenario: Escalation and denial are both triggered
- **GIVEN** one or more checks trigger escalation and one or more checks trigger denial
- **WHEN** the agent selects the final recommendation decision
- **THEN** the final decision is `escalate`

#### Scenario: Denial without escalation
- **GIVEN** no escalation condition is present
- **AND** one or more checks trigger denial
- **WHEN** the agent selects the final recommendation decision
- **THEN** the final decision is `deny`

#### Scenario: Approval only when no blocking findings exist
- **GIVEN** no escalation condition is present
- **AND** no denial condition is present
- **WHEN** the agent selects the final recommendation decision
- **THEN** the final decision is `approve`

### Requirement: Error handling and safe-fail behavior
The agent SHALL treat tool failures as safety-critical and return a schema-valid recommendation with visible error context.

#### Scenario: Tool exception or error payload
- **GIVEN** any tool raises an exception or returns an explicit `error` field
- **WHEN** the agent finalizes the recommendation
- **THEN** decision is set to `escalate`
- **AND** rationale includes non-empty error context describing the affected tool and failure condition
- **AND** the response remains valid against `ProcurementRecommendation`

### Requirement: Recommendation value and rationale constraints
The agent SHALL produce recommendations with constrained decision values and a non-empty rationale.

#### Scenario: Output guardrails
- **WHEN** the agent emits a recommendation
- **THEN** `decision` is exactly one of `approve`, `deny`, or `escalate`
- **AND** `rationale` is a non-empty string after trimming whitespace

### Requirement: System prompt policy and behavioral constraints
The system prompt used by `agent.py` SHALL encode mandatory behavior for tool usage, decision policy, and rationale quality.

#### Scenario: Prompt enforces complete tool usage
- **WHEN** the model is instructed by the system prompt
- **THEN** it is required to call all four tools for every request
- **AND** it is prohibited from short-circuiting after a single finding

#### Scenario: Prompt enforces decision policy
- **WHEN** the model synthesizes a recommendation from tool outputs
- **THEN** it applies strict decision precedence (`escalate > deny > approve`)
- **AND** it does not emit decisions outside the allowed set

#### Scenario: Prompt enforces rationale quality
- **WHEN** the model generates rationale
- **THEN** rationale includes concrete decision drivers from checks (for example policy IDs, risk level, or budget overage)
- **AND** rationale is explicit about uncertainty or missing data when tool errors occur
- **AND** rationale remains non-empty and actionable for procurement reviewers

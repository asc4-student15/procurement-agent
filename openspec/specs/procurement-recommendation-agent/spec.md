## Purpose

Define orchestration and final recommendation decision behavior for procurement requests using four required checks and structured agent output.

## ADDED Requirements

### Requirement: Four-Check Recommendation Flow
The system SHALL run budget, vendor-duplication, policy-compliance, and risk-assessment checks for each purchase request before final recommendation.

#### Scenario: Request processed through all checks
- **WHEN** a valid purchase request is evaluated
- **THEN** all four checks are executed and their findings are available to recommendation logic

### Requirement: Decision Priority Resolution
The system MUST resolve recommendation decisions with precedence order escalate, then deny, then approve.

#### Scenario: Escalate and deny signals both present
- **WHEN** at least one escalate condition and at least one deny condition are returned by checks
- **THEN** the final decision is escalate

#### Scenario: Deny signal without escalate condition
- **WHEN** one or more deny conditions are returned and no escalate condition exists
- **THEN** the final decision is deny

#### Scenario: No deny or escalate conditions
- **WHEN** all checks return approval-safe results
- **THEN** the final decision is approve

### Requirement: Error Reflection in Rationale
The system SHALL include tool error information in rationale text and SHALL not approve when required check data is unavailable.

#### Scenario: Tool failure during evaluation
- **WHEN** any check returns an error payload
- **THEN** rationale references the error context and the recommendation is escalate

### Requirement: Structured Agent Output
The system SHALL construct the agent with structured output type ProcurementRecommendation rather than free-form text.

#### Scenario: Agent emits recommendation
- **WHEN** the agent returns a result for a valid request
- **THEN** the result conforms to ProcurementRecommendation with non-empty rationale and constrained decision value

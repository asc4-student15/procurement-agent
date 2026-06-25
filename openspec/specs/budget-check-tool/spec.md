# Capability: budget-check-tool

## Purpose
TBD: Synced from change 'add-procurement-intelligence-agent'.

## Requirements

### Requirement: Budget sufficiency calculation
`check_budget(cost_center_id, total_amount)` MUST return whether the request is within remaining budget and include overage amount when not within budget.

#### Scenario: Over-budget request
- **WHEN** a request total exceeds the cost center remaining budget
- **THEN** the tool returns `within_budget=false` and `overage > 0`

### Requirement: Unknown cost center handling
The budget tool MUST return a structured error result for unknown cost center IDs.

#### Scenario: Unknown cost center
- **WHEN** a cost center ID does not exist in budget data
- **THEN** the tool returns an `error` field and `within_budget=false`

### Requirement: Stable result and error shape
The budget tool MUST always include `within_budget`, `cost_center_id`, `remaining_budget`, `requested_amount`, and `overage`.

On error, the tool MUST also include `error` and SHOULD preserve the same core keys to support downstream decision logic.

#### Scenario: Successful budget check
- **WHEN** the tool evaluates a valid cost center
- **THEN** the response includes all required keys with typed values

#### Scenario: Budget data load failure
- **WHEN** budget data is unavailable
- **THEN** response includes `error` and the core result keys so the agent can escalate safely


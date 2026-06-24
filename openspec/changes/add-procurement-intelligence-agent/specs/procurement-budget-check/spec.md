## ADDED Requirements

### Requirement: Cost Center Budget Evaluation
The system SHALL provide a budget check that compares requested amount to the cost center remaining quarterly budget and returns within_budget, remaining_budget, requested_amount, and overage values.

#### Scenario: Request within remaining budget
- **WHEN** requested amount is less than or equal to remaining budget for the cost center
- **THEN** the check returns within_budget true and overage 0

#### Scenario: Request exceeds remaining budget
- **WHEN** requested amount is greater than remaining budget for the cost center
- **THEN** the check returns within_budget false and overage equal to the excess amount

### Requirement: Unknown Cost Center Handling
The system SHALL return a structured error payload when a cost center id is not present in budget data.

#### Scenario: Cost center not found
- **WHEN** budget check is called with an unknown cost_center_id
- **THEN** the result includes an error message and a non-approval-safe status

## ADDED Requirements

### Requirement: PurchaseRequest field coverage and typing
The system MUST define a Pydantic v2 `PurchaseRequest` model with exactly these required fields from request payloads: `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`, `category`, `item_description`, `quantity`, `unit_price`, and `total_amount`.

The system MUST treat `expected_outcome` and `outcome_reason` as fixture-only reference fields and MUST NOT require them in the runtime `PurchaseRequest` schema.

#### Scenario: Reject missing required request field
- **WHEN** a request omits any required `PurchaseRequest` field
- **THEN** model validation fails and no recommendation is produced from invalid input

#### Scenario: Ignore fixture-only outcome fields
- **WHEN** sample data includes `expected_outcome` and `outcome_reason`
- **THEN** those fields are treated as fixture metadata and are not required runtime inputs

### Requirement: Numeric validators for request values
The `PurchaseRequest` model MUST apply numeric validation such that `quantity > 0`, `unit_price > 0`, and `total_amount > 0`.

The model SHOULD validate that `total_amount` is consistent with `quantity * unit_price` (allowing a small currency rounding tolerance).

#### Scenario: Reject non-positive numeric inputs
- **WHEN** quantity, unit price, or total amount is zero or negative
- **THEN** model validation fails with field-level errors

#### Scenario: Reject inconsistent computed total
- **WHEN** `total_amount` materially differs from `quantity * unit_price`
- **THEN** model validation fails with a total consistency error

### Requirement: ProcurementRecommendation model constraints
The system MUST define a Pydantic v2 `ProcurementRecommendation` model with fields `request_id`, `decision`, and `rationale`, where `decision` is constrained to exactly `approve`, `deny`, or `escalate`.

#### Scenario: Enforce decision enum
- **WHEN** a recommendation is created with decision value outside `approve`, `deny`, or `escalate`
- **THEN** model validation fails

### Requirement: Non-empty rationale enforcement
The system MUST reject any `ProcurementRecommendation` with an empty or whitespace-only rationale string.

#### Scenario: Reject blank rationale
- **WHEN** a recommendation is created with rationale set to empty string or whitespace
- **THEN** model validation fails with a rationale validation error
## ADDED Requirements

### Requirement: Purchase Request Schema Validation
The system SHALL define a PurchaseRequest model with typed fields for request_id, requestor, cost_center_id, vendor_name, vendor_id, category, item_description, quantity, unit_price, and total_amount.

#### Scenario: Valid purchase request accepted
- **WHEN** a request payload includes all required fields with valid types and positive numeric amounts
- **THEN** the payload is accepted as a valid PurchaseRequest instance

#### Scenario: Invalid amount rejected
- **WHEN** a request payload provides a non-positive total_amount or unit_price
- **THEN** model validation fails and the request is rejected before recommendation processing

### Requirement: Recommendation Schema Constraints
The system SHALL define a ProcurementRecommendation model with request_id, decision, and rationale, where decision MUST be one of approve, deny, or escalate and rationale MUST be non-empty.

#### Scenario: Valid recommendation output
- **WHEN** the agent returns a decision in the allowed set with a non-empty rationale
- **THEN** the output validates as a ProcurementRecommendation instance

#### Scenario: Invalid decision blocked
- **WHEN** recommendation output contains a decision value outside approve, deny, or escalate
- **THEN** output validation fails and the invalid recommendation is not accepted

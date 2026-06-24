## ADDED Requirements

### Requirement: Vendor duplication input contract
`check_vendor_duplication(vendor_id, category, total_amount)` MUST accept vendor ID, purchase category, and total request amount.

The check MUST determine whether another vendor (different from `vendor_id`) has an active contract in the same category.

#### Scenario: Detect category peer vendors
- **WHEN** the requested vendor has category peers with active contracts
- **THEN** those peers are identified as potential conflicts

### Requirement: POL-001 threshold and deny trigger
The tool MUST apply POL-001 single-source threshold logic where conflict-driven denial is only triggered when `total_amount > 25000`.

#### Scenario: Below threshold request
- **WHEN** total amount is less than or equal to $25,000
- **THEN** the tool returns `violation=false` and explains threshold non-applicability under POL-001

#### Scenario: Above-threshold conflict triggers deny path
- **WHEN** `total_amount > 25000` and at least one conflicting active-contract vendor exists in the same category
- **THEN** the tool returns `violation=true` and reason text indicating POL-001 denial trigger

### Requirement: Active contract conflict detection
For threshold-eligible requests, the tool MUST detect conflicting active vendors in the same category.

#### Scenario: Conflicting vendor exists
- **WHEN** another active vendor exists in the request category and amount is above threshold
- **THEN** the tool returns `violation=true` with conflicting vendor IDs and names

### Requirement: Conflict contract details in return shape
The tool MUST always return `conflicting_vendor_ids` and `conflicting_contract_details`.

Each entry in `conflicting_contract_details` MUST include at least:
- `vendor_id`
- `vendor_name`
- `contract_id`
- `contract_status`
- `category`

#### Scenario: Return structured conflict contract details
- **WHEN** one or more conflicting active-contract vendors are identified
- **THEN** `conflicting_contract_details` includes the required contract fields for each conflicting vendor

### Requirement: Stable result and error shape
The tool MUST always return keys: `violation`, `vendor_id`, `category`, `amount`, `conflicting_vendor_ids`, `conflicting_contract_details`, and `reason`.

When vendor data cannot be loaded, the tool MUST include `error` and SHOULD preserve all standard keys.

#### Scenario: Vendor data unavailable
- **WHEN** vendor data loading fails
- **THEN** the tool returns an `error` field and preserves response keys for downstream handling
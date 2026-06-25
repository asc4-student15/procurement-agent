# Capability: risk-assessment-tool

## Purpose
TBD: Synced from change 'add-procurement-intelligence-agent'.

## Requirements

### Requirement: Risk profile input and output contract
`assess_risk(vendor_id)` MUST accept a vendor ID and return a vendor risk profile containing:
- compliance flag status
- contract status
- computed risk level

#### Scenario: Return risk profile for known vendor
- **WHEN** a valid vendor ID is provided
- **THEN** the tool returns compliance flag status, contract status, and computed risk level

### Requirement: Vendor risk classification
The tool MUST compute risk level from vendor compliance and contract state using exactly: `low`, `medium`, `high`, `critical`.

#### Scenario: Compliance-flagged vendor
- **WHEN** vendor has `compliance_flag=true`
- **THEN** risk level is `critical`

### Requirement: Unknown vendor fallback
The tool MUST return an error result for unknown vendor IDs while preserving a structured response shape.

#### Scenario: Vendor not found
- **WHEN** vendor ID is absent from vendor records
- **THEN** result includes `error` and a non-empty risk summary

### Requirement: Risk response completeness
The tool MUST always include `vendor_id`, `vendor_name`, `compliance_flag`, `compliance_notes`, `contract_status`, `risk_level`, and `risk_summary`.

On data access failures, the tool MUST include `error` and SHOULD preserve all standard response keys.

#### Scenario: Active contracted vendor
- **WHEN** vendor has active contract and no compliance issues
- **THEN** risk level is `low` and summary explains why

#### Scenario: Return complete risk profile
- **WHEN** vendor data is available
- **THEN** response includes compliance flag status, contract status, and one computed risk level in `low|medium|high|critical`


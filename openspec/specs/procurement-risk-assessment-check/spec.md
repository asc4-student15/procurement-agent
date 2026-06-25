## Purpose

Define vendor risk classification behavior and safe error handling for missing or unknown vendor data.

## ADDED Requirements

### Requirement: Vendor Risk Classification
The system SHALL compute vendor risk_level using compliance and contract status signals with possible values low, medium, high, and critical.

#### Scenario: Critical risk for flagged vendor
- **WHEN** vendor compliance_flag is true
- **THEN** risk_level is critical and summary indicates Legal and Compliance escalation requirement

#### Scenario: High risk for expired contract
- **WHEN** vendor contract status is expired and no compliance flag is present
- **THEN** risk_level is high and summary indicates contract renewal is required

#### Scenario: Medium risk for no contract
- **WHEN** vendor contract status is none and no compliance flag is present
- **THEN** risk_level is medium and summary advises procurement verification

### Requirement: Missing Vendor Error Handling
The system SHALL provide a structured high-risk or critical-risk result when vendor lookup fails due to missing data or unknown vendor id.

#### Scenario: Unknown vendor id
- **WHEN** risk assessment is called with a vendor id not found in vendor records
- **THEN** the result includes an error message and non-low risk classification

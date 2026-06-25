## Purpose

Define centralized access patterns for procurement mock datasets so tools use consistent loader APIs and explicit missing-file handling.

## ADDED Requirements

### Requirement: Centralized Mock Data Access
The system SHALL provide loader functions that return parsed records from budgets, vendors, policies, and requests datasets.

#### Scenario: Load budgets through loader
- **WHEN** budget data is requested by a tool
- **THEN** the tool receives budget records through the data loader function rather than direct file access

### Requirement: No Direct Mock Data Reads in Tools
The system MUST ensure tool modules access mock data only through data loader APIs.

#### Scenario: Tool accesses vendor data
- **WHEN** a tool needs vendor records for policy or risk checks
- **THEN** the tool calls the data loader vendor function and does not open mock data files directly

### Requirement: Structured Missing-File Failure
The system SHALL raise or propagate a structured file-missing error when a referenced dataset is unavailable.

#### Scenario: Missing policies dataset
- **WHEN** the policies file is not present at expected path
- **THEN** the loader surfaces a file-not-found error that the calling tool can handle explicitly

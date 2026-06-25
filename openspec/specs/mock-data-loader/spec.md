# Capability: mock-data-loader

## Purpose
TBD: Synced from change 'add-procurement-intelligence-agent'.

## Requirements

### Requirement: Loader-only mock data access
The system SHALL read all reference mock data through `data/loader.py` and SHALL NOT read `mock_data/*.json` directly from tool modules.

#### Scenario: Tool retrieves data through loader
- **WHEN** any tool requires budgets, vendors, policies, or sample requests
- **THEN** the tool calls a loader function from `data/loader.py`

### Requirement: Structured data loading API
The system SHALL provide dedicated loader functions for budgets, vendors, policies, and requests, each returning parsed JSON records as lists of dictionaries.

#### Scenario: Load vendor records
- **WHEN** the vendor loader is invoked
- **THEN** it returns parsed vendor records from `mock_data/vendors.json` as a list

### Requirement: Missing file error signaling
The loader SHALL raise a clear file-not-found error when a required mock data file is unavailable.

#### Scenario: Missing policies file
- **WHEN** the policies file path does not exist
- **THEN** the loader raises `FileNotFoundError` with path context


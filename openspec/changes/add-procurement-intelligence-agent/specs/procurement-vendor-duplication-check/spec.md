## ADDED Requirements

### Requirement: Single-Source Violation Detection
The system SHALL detect vendor-duplication violations for covered categories when request amount exceeds the single-source threshold and active contracted alternatives exist.

#### Scenario: Above-threshold non-contracted request in covered category
- **WHEN** request amount is above threshold and active contracted vendors exist in the same category excluding the requested vendor
- **THEN** the check returns violation true with conflicting vendor identifiers

#### Scenario: Below-threshold request
- **WHEN** request amount is at or below the single-source threshold
- **THEN** the check returns violation false for threshold-based single-source enforcement

### Requirement: Human-Readable Violation Reason
The system SHALL include a reason string describing whether a duplication violation was found and why.

#### Scenario: Violation explanation includes threshold and conflicts
- **WHEN** a single-source violation is detected
- **THEN** the reason states the threshold basis and identifies contracted conflicting vendors

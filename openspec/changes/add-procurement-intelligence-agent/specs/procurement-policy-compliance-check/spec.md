## ADDED Requirements

### Requirement: Multi-Policy Evaluation Result
The system SHALL evaluate each request against procurement policies and return a list of triggered violations, each containing policy_id, rule_description, and forced_decision.

#### Scenario: Prohibited catering request
- **WHEN** a request category is catering
- **THEN** a violation is returned with forced_decision deny under the catering prohibition policy

#### Scenario: Compliance-flagged vendor request
- **WHEN** a request references a vendor with an active compliance flag
- **THEN** a violation is returned with forced_decision escalate under compliance hold policy

### Requirement: Approval Threshold Governance
The system SHALL flag requests at or above the director threshold for escalation and SHALL flag near-threshold requests according to governance rules.

#### Scenario: Director threshold reached
- **WHEN** request amount is greater than or equal to the director threshold
- **THEN** the result includes an escalation-forcing policy violation

#### Scenario: Near-director-threshold request
- **WHEN** request amount falls within defined near-threshold band below the director threshold
- **THEN** the result includes an escalation-forcing governance violation

### Requirement: Compliance Check Error Safety
The system SHALL return a structured error outcome when policy or vendor data cannot be loaded.

#### Scenario: Policy data unavailable
- **WHEN** the compliance checker cannot load required datasets
- **THEN** the output includes an error indicator and escalation-safe severity

## ADDED Requirements

### Requirement: Medium Risk Does Not Force Escalation
The system SHALL treat risk_level medium as advisory context and SHALL NOT classify medium risk alone as an escalation trigger.

#### Scenario: Deny policy with medium vendor risk
- **WHEN** a request has at least one deny-level finding and risk assessment returns risk_level medium with no tool/data error and no escalate-forcing policy signal
- **THEN** the final decision is deny

### Requirement: Escalation Triggers Remain Strictly Enforced
The system MUST escalate when any escalate-forcing condition exists, including tool/data errors, critical vendor risk, or policy violations with forced_decision escalate.

#### Scenario: Compliance-flagged vendor
- **WHEN** a request includes a vendor with compliance_flag true that produces critical risk or policy forced escalation
- **THEN** the final decision is escalate

#### Scenario: Tool data unavailable
- **WHEN** any required check returns an error payload
- **THEN** the final decision is escalate and rationale references the error context

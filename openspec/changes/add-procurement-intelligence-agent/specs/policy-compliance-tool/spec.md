## ADDED Requirements

### Requirement: Purchase-request policy evaluation scope
`check_policy_compliance(vendor_id, category, total_amount, quantity)` MUST evaluate the request against all eight policies defined in `mock_data/policies.json`.

The evaluation MUST consider request attributes and relevant vendor context.

#### Scenario: Full policy sweep
- **WHEN** a request is submitted for policy evaluation
- **THEN** all eight policies are checked, not only category-specific shortcuts

### Requirement: Policy violation reporting
The tool MUST return all triggered policy violations with `policy_id`, `rule_description`, and forced decision (`deny` or `escalate`).

#### Scenario: Catering prohibition
- **WHEN** category is `catering`
- **THEN** violations include `POL-004` with forced decision `deny`

#### Scenario: No violations found
- **WHEN** no policy rules are violated
- **THEN** `violations` is an empty list and `violation_count` is `0`

### Requirement: Severity prioritization output
The tool MUST compute `highest_severity` as `escalate` if any escalation policy is triggered, otherwise `deny` if any deny policy is triggered, otherwise `none`.

#### Scenario: Mixed deny and escalate violations
- **WHEN** violations include at least one `deny` and at least one `escalate`
- **THEN** `highest_severity` is `escalate`

### Requirement: Stable result and error shape
The tool MUST always return `violations`, `violation_count`, and `highest_severity`.

Each item in `violations` MUST include exactly the contract fields:
- `policy_id`
- `rule_description`
- `forced_decision`

If policy or vendor data cannot be loaded, the tool MUST include `error` and SHOULD set `highest_severity` to escalation-safe behavior.

#### Scenario: Policy data unavailable
- **WHEN** policy or vendor data loading fails
- **THEN** result includes `error` and sets severity to escalation-safe behavior
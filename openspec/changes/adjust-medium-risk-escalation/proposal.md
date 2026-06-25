## Why

REQ-009 currently resolves to escalate even though the sample dataset and solution behavior expect deny for catering prohibition (POL-004). This happens because medium vendor risk is treated as an escalation trigger and globally outranks deny-level policy findings.

## What Changes

- Update recommendation decision rules so medium risk alone does not force escalation.
- Preserve escalation for critical risk, explicit policy escalation triggers, near-director-threshold governance, and tool/data errors.
- Ensure deny-level policy outcomes (for example POL-004 catering prohibition) resolve to deny when no true escalation trigger is present.
- Add and align tests for REQ-009 deny while preserving REQ-011 escalate.

## Capabilities

### New Capabilities
- `recommendation-decision-risk-precedence`: Defines how risk levels interact with deny and escalate signals so medium risk is advisory unless coupled with an escalation policy trigger.

### Modified Capabilities
- None.

## Impact

- Affected code: [agent.py](agent.py) decision aggregation logic and rationale shaping.
- Affected tests: [tests/test_agent.py](tests/test_agent.py) and any decision-priority regression tests.
- No new external dependencies or API surface changes.

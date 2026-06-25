## 1. Models

- [ ] 1.1 Define `PurchaseRequest` with all required runtime fields from request payloads.
- [ ] 1.2 Add numeric validators (`quantity`, `unit_price`, `total_amount` > 0).
- [ ] 1.3 Add consistency validation for `total_amount ~= quantity * unit_price`.
- [ ] 1.4 Define `ProcurementRecommendation` with `request_id`, `decision`, `rationale`.
- [ ] 1.5 Constrain `decision` to `approve | deny | escalate`.
- [ ] 1.6 Enforce non-empty rationale.

## 2. Data Loader

- [ ] 2.1 Implement `data/loader.py` as the only mock data access layer.
- [ ] 2.2 Add loader functions for budgets, vendors, policies, and requests.
- [ ] 2.3 Raise clear `FileNotFoundError` when a required mock file is missing.

## 3. Tool: check_budget

- [ ] 3.1 Implement `check_budget(cost_center_id, total_amount)`.
- [ ] 3.2 Return required keys: `within_budget`, `cost_center_id`, `remaining_budget`, `requested_amount`, `overage`.
- [ ] 3.3 Return structured `error` for unknown cost center or load failures.

## 4. Tool: check_vendor_duplication

- [ ] 4.1 Implement `check_vendor_duplication(vendor_id, category, total_amount)`.
- [ ] 4.2 Apply POL-001 only when amount is greater than $25,000.
- [ ] 4.3 Return required keys and conflict details for active-category duplicates.
- [ ] 4.4 Return structured `error` while preserving standard keys on data failures.

## 5. Tool: check_policy_compliance

- [ ] 5.1 Implement `check_policy_compliance(vendor_id, category, total_amount, quantity)`.
- [ ] 5.2 Return violations with `policy_id`, `rule_description`, `forced_decision`.
- [ ] 5.3 Compute `highest_severity` with `escalate > deny > none` ordering.
- [ ] 5.4 Return structured `error` with escalation-safe severity on data failures.

## 6. Tool: assess_risk

- [ ] 6.1 Implement `assess_risk(vendor_id)`.
- [ ] 6.2 Map risk levels to `low | medium | high | critical` from vendor attributes.
- [ ] 6.3 Return required risk keys and non-empty `risk_summary`.
- [ ] 6.4 Return structured `error` while preserving standard keys on data failures.

## 7. Agent Wiring and Decision Logic

- [ ] 7.1 Construct Pydantic AI agent with `output_type=ProcurementRecommendation`.
- [ ] 7.2 Wire all four tools and execute each for every request.
- [ ] 7.3 Implement decision priority `escalate > deny > approve`.
- [ ] 7.4 Force `escalate` when any tool returns `error`.
- [ ] 7.5 Ensure rationale references driving checks and any tool error context.

## 8. Verification and Records

- [ ] 8.1 Validate change artifacts with `openspec validate --changes`.
- [ ] 8.2 Run `pytest tests/ -v --tb=short --junitxml=docs/test-results.xml`.
- [ ] 8.3 Confirm recommendation outputs are always schema-valid.
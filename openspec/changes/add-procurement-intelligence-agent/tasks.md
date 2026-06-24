## 1. Models and Data Access

- [ ] 1.1 Implement PurchaseRequest and ProcurementRecommendation Pydantic v2 models with decision constrained to approve, deny, or escalate.
- [ ] 1.2 Add model validation for non-empty rationale and positive numeric request amounts.
- [ ] 1.3 Implement data loader functions for budgets, vendors, policies, and requests under data/loader.py.
- [ ] 1.4 Ensure tool modules use data loader APIs and do not read mock_data files directly.

## 2. Tool Implementations

- [ ] 2.1 Implement check_budget to return within_budget, remaining_budget, requested amount, and overage.
- [ ] 2.2 Implement check_vendor_duplication with single-source threshold logic and conflicting vendor details.
- [ ] 2.3 Implement check_policy_compliance to evaluate policy violations with policy_id, rule description, and forced decision.
- [ ] 2.4 Implement assess_risk to compute risk level from compliance flag and contract status.
- [ ] 2.5 Implement structured error outputs for all tools so failures can be surfaced to recommendation logic.

## 3. Agent Orchestration and Decisioning

- [ ] 3.1 Construct the Pydantic AI agent with output_type set to ProcurementRecommendation.
- [ ] 3.2 Wire all four tools into the agent and require all checks to run for each request.
- [ ] 3.3 Implement decision precedence logic: escalate over deny over approve.
- [ ] 3.4 Ensure tool errors are reflected in rationale and drive safe escalation behavior.
- [ ] 3.5 Include request_id propagation and clear rationale requirements in agent response guidance.

## 4. Tests and Verification

- [ ] 4.1 Add tool unit tests covering primary success paths for budget, duplication, policy, and risk checks.
- [ ] 4.2 Add agent integration tests covering approve, deny, and escalate outcomes using sample requests.
- [ ] 4.3 Add at least one partial-data or missing-data scenario proving error-to-escalation behavior.
- [ ] 4.4 Run full test suite and generate docs/test-results.xml for ITC.003 evidence.
- [ ] 4.5 Run openspec validate for the change and confirm artifacts remain coherent.

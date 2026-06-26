"""Run the agent against all 15 sample requests and compare to expected outcomes."""

from __future__ import annotations

import asyncio

from agent import agent, build_request_prompt
from data.loader import load_requests
from models import PurchaseRequest


async def main() -> None:
    requests_data = load_requests()

    results = {"approve": 0, "deny": 0, "escalate": 0, "mismatch": 0}

    for req_data in requests_data:
        expected = str(req_data["expected_outcome"])
        request = PurchaseRequest(
            **{
                k: v
                for k, v in req_data.items()
                if k not in {"expected_outcome", "outcome_reason"}
            }
        )

        raw_result = await agent.run(build_request_prompt(request))
        decision = raw_result.output.decision
        if expected == "ambiguous":
            is_match = True
        else:
            is_match = decision == expected
        match = "OK" if is_match else "X"

        results[decision] += 1
        if not is_match:
            results["mismatch"] += 1

        print(f"{match} {req_data['request_id']}: expected={expected}, got={decision}")
        print(f"  Rationale: {raw_result.output.rationale[:80]}...")
        print()

    print(
        f"\nSummary: approve={results['approve']} deny={results['deny']} "
        f"escalate={results['escalate']} mismatches={results['mismatch']}"
    )


if __name__ == "__main__":
    asyncio.run(main())

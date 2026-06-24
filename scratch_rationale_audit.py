"""Audit agent rationale quality against template criteria for all sample requests."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass

from agent import agent, build_request_prompt
from data.loader import load_requests
from models import PurchaseRequest, ProcurementRecommendation

_POLICY_PATTERN = re.compile(r"\bPOL-\d{3}\b")
_AMOUNT_PATTERN = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?\b|\b\d[\d,]*(?:\.\d{1,2})?\b")

_CHECK_KEYWORDS = (
    "budget",
    "check_budget",
    "policy",
    "pol-",
    "risk",
    "assess_risk",
    "duplication",
    "check_vendor_duplication",
    "check_policy_compliance",
)


@dataclass
class AuditResult:
    request_id: str
    decision: str
    rationale: str
    failures: list[str]


def sentence_count(text: str) -> int:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    return len(sentences)


def has_check_reference(rationale: str) -> bool:
    lowered = rationale.lower()
    return any(keyword in lowered for keyword in _CHECK_KEYWORDS)


def has_context_details(rationale: str, vendor_name: str) -> bool:
    has_policy = bool(_POLICY_PATTERN.search(rationale))
    has_amount = bool(_AMOUNT_PATTERN.search(rationale))
    has_vendor = vendor_name.lower() in rationale.lower()
    return has_policy or has_amount or has_vendor


def has_bullets(rationale: str) -> bool:
    lines = [line.strip() for line in rationale.splitlines() if line.strip()]
    return any(line.startswith(("-", "*", "1.", "2.", "3.")) for line in lines)


def audit_rationale(rec: ProcurementRecommendation, vendor_name: str) -> list[str]:
    failures: list[str] = []
    rationale = rec.rationale.strip()

    if not rationale:
        failures.append("empty rationale")
        return failures

    if has_bullets(rationale):
        failures.append("contains bullet formatting")

    count = sentence_count(rationale)
    if count < 2 or count > 4:
        failures.append(f"sentence count out of range: {count}")

    if not has_check_reference(rationale):
        failures.append("missing named decision-driving check")

    if not has_context_details(rationale, vendor_name):
        failures.append("missing amount/vendor/policy context")

    # Flag vague phrases that often omit actionable context.
    vague_phrases = (
        "policy issues",
        "multiple violations",
        "requires review",
        "cannot be proceeded",
        "further evaluation",
    )
    lowered = rationale.lower()
    if any(phrase in lowered for phrase in vague_phrases) and not _POLICY_PATTERN.search(rationale):
        failures.append("vague policy language without policy IDs")

    return failures


async def run_audit() -> list[AuditResult]:
    records = load_requests()
    results: list[AuditResult] = []

    for record in records:
        request = PurchaseRequest(
            request_id=str(record["request_id"]),
            requestor=str(record["requestor"]),
            cost_center_id=str(record["cost_center_id"]),
            vendor_name=str(record["vendor_name"]),
            vendor_id=str(record["vendor_id"]),
            category=str(record["category"]),
            item_description=str(record["item_description"]),
            quantity=int(record["quantity"]),
            unit_price=float(record["unit_price"]),
            total_amount=float(record["total_amount"]),
        )

        run_result = await agent.run(build_request_prompt(request))
        recommendation: ProcurementRecommendation = run_result.output
        failures = audit_rationale(recommendation, request.vendor_name)

        results.append(
            AuditResult(
                request_id=request.request_id,
                decision=recommendation.decision,
                rationale=recommendation.rationale,
                failures=failures,
            )
        )

    return results


def print_report(results: list[AuditResult]) -> int:
    fail_count = 0

    print("Rationale template audit results:")
    for result in results:
        if result.failures:
            fail_count += 1
            print(f"- {result.request_id}: FAIL -> {', '.join(result.failures)}")
            print(f"  decision={result.decision}")
            print(f"  rationale={result.rationale}")
        else:
            print(f"- {result.request_id}: PASS")

    print(f"\nSummary: {len(results) - fail_count}/{len(results)} passed")
    return fail_count


if __name__ == "__main__":
    audit_results = asyncio.run(run_audit())
    failures = print_report(audit_results)
    raise SystemExit(1 if failures else 0)

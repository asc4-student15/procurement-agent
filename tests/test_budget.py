from __future__ import annotations

from tools.budget import check_budget


def test_check_budget_within_and_exceeding_for_cc003() -> None:
    """Verify both within-budget and over-budget outcomes for CC-003 using real mock data."""
    within_result = check_budget("CC-003", 6900.0)
    assert within_result["within_budget"] is True
    assert within_result["remaining_budget"] == 6900.0
    assert within_result["overage"] == 0.0

    over_result = check_budget("CC-003", 11200.0)
    assert over_result["within_budget"] is False
    assert over_result["remaining_budget"] == 6900.0
    assert over_result["overage"] == 4300.0

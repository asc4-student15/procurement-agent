"""Tests for the budget tool using real mock data."""

from __future__ import annotations

from tools.budget import check_budget


def test_check_budget_within_and_over_budget_for_cc003() -> None:
    """CC-003 should pass at remaining budget and fail when exceeded."""
    within_result = check_budget("CC-003", 6_900.00)
    assert within_result["within_budget"] is True
    assert within_result["overage"] == 0.0

    over_result = check_budget("CC-003", 11_200.00)
    assert over_result["within_budget"] is False
    assert over_result["overage"] == 4_300.0

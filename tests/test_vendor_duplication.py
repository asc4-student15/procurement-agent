"""Tests for vendor duplication detection using real mock data."""

from __future__ import annotations

from tools.vendor_duplication import check_vendor_duplication


def test_req008_vendor_duplication_conflicts() -> None:
    """REQ-008 should detect active office supplies contract conflicts."""
    result = check_vendor_duplication("V-012", "office_supplies", 28_500.0)

    assert result["violation"] is True
    assert set(result["conflicting_vendor_ids"]) == {"V-001", "V-003"}

from __future__ import annotations

from tools.vendor_duplication import check_vendor_duplication


def test_req008_vendor_duplication_conflicts() -> None:
    """REQ-008: NovaPrint office_supplies at $28,500 should conflict with V-001 and V-003."""
    result = check_vendor_duplication(
        vendor_id="V-012",
        category="office_supplies",
        amount=28500.0,
    )

    assert result["violation"] is True
    assert set(result["conflicting_vendor_ids"]) == {"V-001", "V-003"}


def test_active_contracted_requested_vendor_is_not_pol001_violation() -> None:
    """REQ-014 pattern: active contracted requested vendor should not trigger POL-001."""
    result = check_vendor_duplication(
        vendor_id="V-016",
        category="hardware",
        amount=47500.0,
    )

    assert result["violation"] is False
    assert result["conflicting_vendor_ids"] == []


def test_vendor_duplication_category_is_case_insensitive() -> None:
    """Mixed-case category values should evaluate the same as lowercase categories."""
    result = check_vendor_duplication(
        vendor_id="V-016",
        category="Hardware",
        amount=47500.0,
    )

    assert result["violation"] is False
    assert result["category"] == "hardware"

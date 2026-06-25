from __future__ import annotations

from tools.risk_assessment import assess_risk


def test_assess_risk_returns_low_for_active_unflagged_vendor() -> None:
    """V-002 is active and unflagged, so risk should be low."""
    result = assess_risk("V-002")

    assert result["vendor_id"] == "V-002"
    assert result["compliance_flag"] is False
    assert result["contract_status"] == "active"
    assert result["risk_level"] == "low"
    assert "error" not in result


def test_assess_risk_returns_medium_for_no_contract_vendor() -> None:
    """V-004 has no contract and no compliance flag, so risk should be medium."""
    result = assess_risk("V-004")

    assert result["vendor_id"] == "V-004"
    assert result["compliance_flag"] is False
    assert result["contract_status"] == "none"
    assert result["risk_level"] == "medium"


def test_assess_risk_returns_high_for_expired_contract_vendor() -> None:
    """V-010 has an expired contract and no compliance flag, so risk should be high."""
    result = assess_risk("V-010")

    assert result["vendor_id"] == "V-010"
    assert result["compliance_flag"] is False
    assert result["contract_status"] == "expired"
    assert result["risk_level"] == "high"


def test_assess_risk_returns_critical_for_compliance_flagged_vendor() -> None:
    """V-006 has an active compliance flag, so risk should be critical."""
    result = assess_risk("V-006")

    assert result["vendor_id"] == "V-006"
    assert result["compliance_flag"] is True
    assert result["risk_level"] == "critical"


def test_assess_risk_unknown_vendor_returns_error_and_non_low_risk() -> None:
    """Unknown vendor IDs must return an error and a non-low risk level."""
    result = assess_risk("V-999")

    assert "error" in result
    assert result["vendor_id"] == "V-999"
    assert result["risk_level"] in {"high", "critical"}

from __future__ import annotations

from typing import Literal, TypedDict

from data import loader as data_loader


class RiskAssessmentResult(TypedDict):
    vendor_id: str
    compliance_flag: bool
    contract_status: str
    risk_level: str
    risk_summary: str


class RiskAssessmentErrorResult(TypedDict):
    error: str
    error_type: Literal["file_not_found", "key_error", "unexpected_error"]
    error_source: str
    vendor_id: str
    compliance_flag: bool
    contract_status: str
    risk_level: str
    risk_summary: str


def _error_result(
    *,
    error_type: Literal["file_not_found", "key_error", "unexpected_error"],
    message: str,
    vendor_id: str,
    risk_level: str,
    risk_summary: str,
) -> RiskAssessmentErrorResult:
    """Build a consistent typed risk-assessment error payload."""
    return {
        "error": message,
        "error_type": error_type,
        "error_source": "risk_assessment",
        "vendor_id": vendor_id,
        "compliance_flag": False,
        "contract_status": "unknown",
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }


def assess_risk(vendor_id: str) -> RiskAssessmentResult | RiskAssessmentErrorResult:
    """Return a vendor risk profile from compliance and contract status signals.

    Risk level rules:
    - critical: compliance_flag is True
    - high: contract_status is "expired" and compliance_flag is False
    - medium: contract_status is "none" and compliance_flag is False
    - low: contract_status is "active" and compliance_flag is False

    Args:
        vendor_id: Vendor identifier from a purchase request.

    Returns:
        A dictionary containing vendor_id, compliance_flag, contract_status,
        computed risk_level, and a risk_summary.

        If vendor data cannot be loaded, or the vendor_id is unknown, returns a
        structured error payload with non-low risk classification.
    """
    try:
        vendors = data_loader.load_vendors()
    except FileNotFoundError as exc:
        return _error_result(
            error_type="file_not_found",
            message=f"Vendor data could not be loaded: {exc}",
            vendor_id=vendor_id,
            risk_level="critical",
            risk_summary="Vendor data unavailable. Treat as critical risk.",
        )
    except KeyError as exc:
        return _error_result(
            error_type="key_error",
            message=f"Vendor data is missing required key: {exc}",
            vendor_id=vendor_id,
            risk_level="critical",
            risk_summary="Vendor data malformed. Treat as critical risk.",
        )
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return _error_result(
            error_type="unexpected_error",
            message=f"Unexpected risk assessment failure: {exc}",
            vendor_id=vendor_id,
            risk_level="critical",
            risk_summary="Risk data processing failed unexpectedly.",
        )

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return _error_result(
            error_type="key_error",
            message=f"Vendor '{vendor_id}' not found in vendor data.",
            vendor_id=vendor_id,
            risk_level="high",
            risk_summary="Unknown vendor. Verify vendor identity before proceeding.",
        )

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none"))

    if compliance_flag:
        risk_level = "critical"
        risk_summary = (
            "Vendor has an active compliance flag and requires Legal and Compliance review."
        )
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = "Vendor contract is expired and requires renewal before purchase."
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = "Vendor has no active contract. Procurement verification is required."
    else:
        risk_level = "low"
        risk_summary = "Vendor has an active contract and no compliance flag."

    return {
        "vendor_id": vendor_id,
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }

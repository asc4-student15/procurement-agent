"""Vendor risk assessment tool for procurement pre-screening."""

from __future__ import annotations

from data.loader import load_vendors


def _error_result(vendor_id: str, error_type: str, error_message: str) -> dict[str, object]:
    """Return a consistent typed error payload for risk assessment failures."""
    return {
        "vendor_id": vendor_id,
        "vendor_name": "Unknown",
        "compliance_flag": False,
        "compliance_notes": "",
        "contract_status": "unknown",
        "risk_level": "critical",
        "risk_summary": "Vendor risk could not be fully evaluated.",
        "error_type": error_type,
        "error": error_message,
    }


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Return a structured risk profile for a vendor.

    Args:
        vendor_id: Vendor identifier from the purchase request.

    Returns:
        A result dictionary that always includes:
        - vendor_id
        - vendor_name
        - compliance_flag
        - compliance_notes
        - contract_status
        - risk_level (low|medium|high|critical)
        - risk_summary

        On data or lookup errors, includes:
        - error
    """
    try:
        vendors = load_vendors()

        vendor = next((v for v in vendors if v.get("vendor_id") == vendor_id), None)
        if vendor is None:
            return {
                "vendor_id": vendor_id,
                "vendor_name": "Unknown",
                "compliance_flag": False,
                "compliance_notes": "",
                "contract_status": "unknown",
                "risk_level": "high",
                "risk_summary": "Vendor not found in records; verification required.",
                "error_type": "lookup_error",
                "error": f"Unknown vendor: {vendor_id}",
            }

        compliance_flag = bool(vendor.get("compliance_flag", False))
        compliance_notes = str(vendor.get("compliance_notes", ""))
        contract_status = str(vendor.get("contract_status", "none"))

        if compliance_flag:
            risk_level = "critical"
            risk_summary = "Vendor has an active compliance flag and requires escalation."
        elif contract_status == "expired":
            risk_level = "high"
            risk_summary = "Vendor contract is expired and presents high procurement risk."
        elif contract_status == "none":
            risk_level = "medium"
            risk_summary = "Vendor has no active contract and requires additional due diligence."
        else:
            risk_level = "low"
            risk_summary = "Vendor is actively contracted with no compliance flags."

        return {
            "vendor_id": vendor_id,
            "vendor_name": str(vendor.get("name", "")),
            "compliance_flag": compliance_flag,
            "compliance_notes": compliance_notes,
            "contract_status": contract_status,
            "risk_level": risk_level,
            "risk_summary": risk_summary,
        }
    except FileNotFoundError as exc:
        return _error_result(vendor_id, "file_not_found", f"Vendor data unavailable: {exc}")
    except KeyError as exc:
        return _error_result(vendor_id, "key_error", f"Vendor data missing required key: {exc}")
    except Exception as exc:
        return _error_result(vendor_id, "unexpected_error", f"Unexpected risk check failure: {exc}")

from __future__ import annotations

from typing import Literal, TypedDict

from data import loader as data_loader

_POL001_THRESHOLD = 25_000.0
_POL001_CONTRACTED_CATEGORIES = {
    "office_supplies",
    "software_licenses",
    "hardware",
    "facilities",
    "security",
    "fleet_parts",
    "staffing",
}


class VendorDuplicationResult(TypedDict):
    violation: bool
    vendor_id: str
    category: str
    amount: float
    conflicting_vendor_ids: list[str]
    reason: str


class VendorDuplicationErrorResult(TypedDict):
    error: str
    error_type: Literal["file_not_found", "key_error", "unexpected_error"]
    error_source: str
    violation: bool
    vendor_id: str
    category: str
    amount: float
    conflicting_vendor_ids: list[str]
    reason: str


def _error_result(
    *,
    error_type: Literal["file_not_found", "key_error", "unexpected_error"],
    message: str,
    vendor_id: str,
    category: str,
    amount: float,
) -> VendorDuplicationErrorResult:
    """Build a consistent typed vendor-duplication error payload."""
    return {
        "error": message,
        "error_type": error_type,
        "error_source": "vendor_duplication",
        "violation": False,
        "vendor_id": vendor_id,
        "category": category,
        "amount": amount,
        "conflicting_vendor_ids": [],
        "reason": "Vendor duplication check could not be completed.",
    }


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    amount: float = 0.0,
) -> VendorDuplicationResult | VendorDuplicationErrorResult:
    """Check for POL-001 single-source vendor duplication violations.

    The check is enforced only when both conditions are true:
    1) The purchase category is a POL-001 contracted category.
    2) The purchase amount exceeds $25,000.

    Args:
        vendor_id: Vendor identifier from the purchase request.
        category: Purchase category from the request.
        amount: Total purchase amount in USD.

    Returns:
        A result dictionary containing:
        - violation: True when a POL-001 violation is detected.
        - vendor_id: Requested vendor identifier.
        - category: Category evaluated.
        - amount: Amount evaluated.
        - conflicting_vendor_ids: Active contracted vendor IDs in the same category,
          excluding the requested vendor.
        - reason: Human-readable explanation of the outcome.

        If vendor data cannot be loaded, returns an error field with a safe
        non-violation result payload.
    """
    try:
        vendors = data_loader.load_vendors()
    except FileNotFoundError as exc:
        return _error_result(
            error_type="file_not_found",
            message=f"Vendor data could not be loaded: {exc}",
            vendor_id=vendor_id,
            category=category,
            amount=amount,
        )
    except KeyError as exc:
        return _error_result(
            error_type="key_error",
            message=f"Vendor data is missing required key: {exc}",
            vendor_id=vendor_id,
            category=category,
            amount=amount,
        )
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return _error_result(
            error_type="unexpected_error",
            message=f"Unexpected vendor duplication check failure: {exc}",
            vendor_id=vendor_id,
            category=category,
            amount=amount,
        )

    normalized_category = category.strip().lower()

    if normalized_category not in _POL001_CONTRACTED_CATEGORIES:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": normalized_category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "reason": (
                f"Category '{normalized_category}' is not in POL-001 contracted categories. "
                "Single-source check does not apply."
            ),
        }

    if amount <= _POL001_THRESHOLD:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": normalized_category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "reason": (
                f"Amount ${amount:,.2f} is at or below ${_POL001_THRESHOLD:,.2f}. "
                "POL-001 does not trigger."
            ),
        }

    requested_vendor_is_active_contracted = any(
        vendor.get("vendor_id") == vendor_id
        and vendor.get("category") == normalized_category
        and vendor.get("contract_status") == "active"
        for vendor in vendors
    )
    if requested_vendor_is_active_contracted:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": normalized_category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "reason": (
                f"Requested vendor '{vendor_id}' is an active contracted vendor in "
                f"category '{normalized_category}'. No POL-001 violation."
            ),
        }

    conflicting_vendor_ids = [
        str(vendor["vendor_id"])
        for vendor in vendors
        if vendor.get("vendor_id") != vendor_id
        and vendor.get("category") == normalized_category
        and vendor.get("contract_status") == "active"
    ]

    if conflicting_vendor_ids:
        return {
            "violation": True,
            "vendor_id": vendor_id,
            "category": normalized_category,
            "amount": amount,
            "conflicting_vendor_ids": conflicting_vendor_ids,
            "reason": (
                f"POL-001 violation: amount ${amount:,.2f} exceeds "
                f"${_POL001_THRESHOLD:,.2f} in contracted category '{normalized_category}', "
                "and active contracted alternatives exist."
            ),
        }

    return {
        "violation": False,
        "vendor_id": vendor_id,
        "category": normalized_category,
        "amount": amount,
        "conflicting_vendor_ids": [],
        "reason": (
            f"No active contracted alternatives found in category '{normalized_category}'. "
            "No POL-001 violation."
        ),
    }

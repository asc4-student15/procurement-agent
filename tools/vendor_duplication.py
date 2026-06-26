"""Vendor duplication check tool for POL-001 single-source restrictions."""

from __future__ import annotations

from data.loader import load_policies, load_vendors

_POL001_THRESHOLD = 25_000.0


def _error_result(
    *,
    vendor_id: str,
    category: str,
    requested_amount: float,
    error_type: str,
    error_message: str,
) -> dict[str, object]:
    """Return a consistent typed error payload for duplication-check failures."""
    return {
        "violation": False,
        "vendor_id": vendor_id,
        "category": category,
        "amount": requested_amount,
        "conflicting_vendor_ids": [],
        "conflicting_contract_details": [],
        "reason": "Vendor or policy data unavailable for duplication check.",
        "error_type": error_type,
        "error": error_message,
    }


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    requested_amount: float = 0.0,
) -> dict[str, object]:
    """Check whether a request conflicts with existing active contracted vendors.

    This tool supports POL-001 single-source enforcement. A violation is only
    triggered when the request amount is greater than $25,000 and the category
    is covered by POL-001 with at least one other active contracted vendor.

    Args:
        vendor_id: Vendor ID requested for the purchase.
        category: Purchase category for the request.
        requested_amount: Total request amount in USD.

    Returns:
        A structured result with keys: violation, vendor_id, category, amount,
        conflicting_vendor_ids, conflicting_contract_details, and reason.
        Includes an error key when vendor or policy data cannot be loaded.
    """
    try:
        vendors = load_vendors()
        policies = load_policies()

        pol001 = next((p for p in policies if p.get("policy_id") == "POL-001"), None)
        affected_categories = set(pol001.get("affected_categories", [])) if pol001 else set()

        requested_vendor = next((v for v in vendors if v.get("vendor_id") == vendor_id), None)
        requested_vendor_is_active_for_category = (
            requested_vendor is not None
            and requested_vendor.get("contract_status") == "active"
            and requested_vendor.get("category") == category
        )

        if requested_amount <= _POL001_THRESHOLD:
            return {
                "violation": False,
                "vendor_id": vendor_id,
                "category": category,
                "amount": requested_amount,
                "conflicting_vendor_ids": [],
                "conflicting_contract_details": [],
                "reason": (
                    f"POL-001 not triggered: amount ${requested_amount:,.2f} is not above "
                    f"${_POL001_THRESHOLD:,.2f}."
                ),
            }

        if category not in affected_categories:
            return {
                "violation": False,
                "vendor_id": vendor_id,
                "category": category,
                "amount": requested_amount,
                "conflicting_vendor_ids": [],
                "conflicting_contract_details": [],
                "reason": f"POL-001 not applicable to category '{category}'.",
            }

        if requested_vendor_is_active_for_category:
            return {
                "violation": False,
                "vendor_id": vendor_id,
                "category": category,
                "amount": requested_amount,
                "conflicting_vendor_ids": [],
                "conflicting_contract_details": [],
                "reason": (
                    "Requested vendor already has an active contract in this category; "
                    "POL-001 conflict is not triggered."
                ),
            }

        conflicts = [
            v for v in vendors
            if v.get("vendor_id") != vendor_id
            and v.get("category") == category
            and v.get("contract_status") == "active"
        ]

        conflict_ids = [str(v.get("vendor_id", "")) for v in conflicts]
        conflict_details = [
            {
                "vendor_id": str(v.get("vendor_id", "")),
                "vendor_name": str(v.get("name", "")),
                "contract_id": str(v.get("contract_id", "")),
                "contract_status": str(v.get("contract_status", "")),
                "category": str(v.get("category", "")),
            }
            for v in conflicts
        ]

        if not conflicts:
            return {
                "violation": False,
                "vendor_id": vendor_id,
                "category": category,
                "amount": requested_amount,
                "conflicting_vendor_ids": [],
                "conflicting_contract_details": [],
                "reason": "No conflicting active contracted vendors found.",
            }

        return {
            "violation": True,
            "vendor_id": vendor_id,
            "category": category,
            "amount": requested_amount,
            "conflicting_vendor_ids": conflict_ids,
            "conflicting_contract_details": conflict_details,
            "reason": (
                "POL-001 violation: active contracted alternatives exist in this "
                "category for an amount above $25,000."
            ),
        }
    except FileNotFoundError as exc:
        return _error_result(
            vendor_id=vendor_id,
            category=category,
            requested_amount=requested_amount,
            error_type="file_not_found",
            error_message=f"Vendor duplication data unavailable: {exc}",
        )
    except KeyError as exc:
        return _error_result(
            vendor_id=vendor_id,
            category=category,
            requested_amount=requested_amount,
            error_type="key_error",
            error_message=f"Vendor duplication data missing required key: {exc}",
        )
    except Exception as exc:
        return _error_result(
            vendor_id=vendor_id,
            category=category,
            requested_amount=requested_amount,
            error_type="unexpected_error",
            error_message=f"Unexpected vendor duplication failure: {exc}",
        )

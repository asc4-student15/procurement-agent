"""Budget validation tool for procurement requests."""

from __future__ import annotations

from data.loader import load_budgets


def _build_error_result(
    *,
    cost_center_id: str,
    requested_amount: float,
    error_type: str,
    error_message: str,
) -> dict[str, object]:
    """Return a consistent typed error payload for budget evaluation failures."""
    return {
        "within_budget": False,
        "cost_center_id": cost_center_id,
        "quarterly_budget": 0.0,
        "remaining_budget": 0.0,
        "remaining_after_purchase": 0.0,
        "requested_amount": requested_amount,
        "overage": requested_amount,
        "error_type": error_type,
        "error": error_message,
    }


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Evaluate whether a request stays within a cost center's remaining budget.

    Args:
        cost_center_id: Cost center identifier from the purchase request.
        requested_amount: Requested purchase amount in USD.

    Returns:
        A result dictionary that always includes:
        - within_budget (bool): Whether requested_amount is within remaining budget.
        - cost_center_id (str): Echoed input cost center ID.
        - quarterly_budget (float): Quarterly budget for the cost center.
        - remaining_budget (float): Remaining budget for the cost center.
        - remaining_after_purchase (float): remaining_budget - requested_amount.
        - requested_amount (float): Echoed input amount.
        - overage (float): Positive amount above remaining budget, else 0.0.

        On error, the result also includes:
        - error (str): Context describing the load or lookup failure.
    """
    try:
        budgets = load_budgets()
        center = next((row for row in budgets if row.get("cost_center_id") == cost_center_id), None)

        if center is None:
            return _build_error_result(
                cost_center_id=cost_center_id,
                requested_amount=requested_amount,
                error_type="lookup_error",
                error_message=f"Unknown cost center: {cost_center_id}",
            )

        remaining_value = center.get("remaining")
        if remaining_value is None:
            remaining_value = center.get("remaining_budget")
        if remaining_value is None:
            return _build_error_result(
                cost_center_id=cost_center_id,
                requested_amount=requested_amount,
                error_type="key_error",
                error_message=(
                    f"Missing remaining budget value for cost center: {cost_center_id}"
                ),
            )

        quarterly_budget = float(center.get("quarterly_budget", 0.0))
        remaining_budget = float(remaining_value)
        remaining_after_purchase = remaining_budget - requested_amount
        overage = max(0.0, requested_amount - remaining_budget)

        return {
            "within_budget": overage == 0.0,
            "cost_center_id": cost_center_id,
            "quarterly_budget": quarterly_budget,
            "remaining_budget": remaining_budget,
            "remaining_after_purchase": remaining_after_purchase,
            "requested_amount": requested_amount,
            "overage": overage,
        }
    except FileNotFoundError as exc:
        return _build_error_result(
            cost_center_id=cost_center_id,
            requested_amount=requested_amount,
            error_type="file_not_found",
            error_message=f"Budget data unavailable: {exc}",
        )
    except KeyError as exc:
        return _build_error_result(
            cost_center_id=cost_center_id,
            requested_amount=requested_amount,
            error_type="key_error",
            error_message=f"Budget data missing required key: {exc}",
        )
    except Exception as exc:
        return _build_error_result(
            cost_center_id=cost_center_id,
            requested_amount=requested_amount,
            error_type="unexpected_error",
            error_message=f"Unexpected budget check failure: {exc}",
        )

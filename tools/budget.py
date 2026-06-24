from __future__ import annotations

from typing import Literal, TypedDict

from data import loader as data_loader


class BudgetCheckResult(TypedDict):
    within_budget: bool
    remaining_budget: float
    requested_amount: float
    overage: float


class BudgetCheckErrorResult(TypedDict):
    error: str
    error_type: Literal["file_not_found", "key_error", "unexpected_error"]
    error_source: str
    within_budget: bool
    remaining_budget: float
    requested_amount: float
    overage: float


def _error_result(
    *,
    error_type: Literal["file_not_found", "key_error", "unexpected_error"],
    message: str,
    requested_amount: float,
) -> BudgetCheckErrorResult:
    """Build a consistent typed budget error payload."""
    return {
        "error": message,
        "error_type": error_type,
        "error_source": "budget",
        "within_budget": False,
        "remaining_budget": 0.0,
        "requested_amount": requested_amount,
        "overage": requested_amount,
    }


def check_budget(
    cost_center_id: str,
    requested_amount: float,
) -> BudgetCheckResult | BudgetCheckErrorResult:
    """Evaluate whether a purchase amount fits within a cost center's remaining budget.

    Args:
        cost_center_id: Cost center identifier from the purchase request.
        requested_amount: Requested purchase amount in USD.

    Returns:
        A dictionary with budget evaluation fields:
        - within_budget: True when requested_amount is less than or equal to remaining budget.
        - remaining_budget: Remaining budget for the cost center.
        - requested_amount: The provided requested amount.
        - overage: Amount above remaining budget (0 when within budget).

        If the cost center is not found, returns a structured error payload with:
        - error: Error description.
        - within_budget: False.
        - remaining_budget: 0.0.
        - requested_amount: The provided requested amount.
        - overage: The full requested amount.
    """
    try:
        budgets = data_loader.load_budgets()

        budget_record = next(
            (item for item in budgets if item.get("cost_center_id") == cost_center_id),
            None,
        )

        if budget_record is None:
            return _error_result(
                error_type="key_error",
                message=f"Cost center '{cost_center_id}' not found in budget data.",
                requested_amount=requested_amount,
            )

        remaining_budget = float(budget_record["remaining"])
        overage = max(0.0, requested_amount - remaining_budget)

        return {
            "within_budget": overage == 0.0,
            "remaining_budget": remaining_budget,
            "requested_amount": requested_amount,
            "overage": overage,
        }
    except FileNotFoundError as exc:
        return _error_result(
            error_type="file_not_found",
            message=f"Budget data could not be loaded: {exc}",
            requested_amount=requested_amount,
        )
    except KeyError as exc:
        return _error_result(
            error_type="key_error",
            message=f"Budget data is missing required key: {exc}",
            requested_amount=requested_amount,
        )
    except Exception as exc:  # pragma: no cover - defensive safeguard
        return _error_result(
            error_type="unexpected_error",
            message=f"Unexpected budget check failure: {exc}",
            requested_amount=requested_amount,
        )

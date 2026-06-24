from __future__ import annotations

import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOCK_DATA_DIR = _PROJECT_ROOT / "mock_data"


def _load_json_list(filename: str) -> list[dict[str, object]]:
    """Load a JSON file from mock_data/ and return its parsed list data."""
    path = _MOCK_DATA_DIR / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_budgets() -> list[dict[str, object]]:
    """Load and return budget records from mock_data/budgets.json."""
    return _load_json_list("budgets.json")


def load_vendors() -> list[dict[str, object]]:
    """Load and return vendor records from mock_data/vendors.json."""
    return _load_json_list("vendors.json")


def load_policies() -> list[dict[str, object]]:
    """Load and return policy records from mock_data/policies.json."""
    return _load_json_list("policies.json")


def load_requests() -> list[dict[str, object]]:
    """Load and return purchase request records from mock_data/requests.json."""
    return _load_json_list("requests.json")

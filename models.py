"""Pydantic v2 models for procurement request input and recommendation output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PurchaseRequest(BaseModel):
    """Runtime purchase request input schema."""

    request_id: str
    requestor: str
    cost_center_id: str
    vendor_name: str
    vendor_id: str
    category: str
    item_description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)


class ProcurementRecommendation(BaseModel):
    """Structured recommendation output schema."""

    request_id: str
    decision: Literal["approve", "deny", "escalate"]
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("rationale")
    @classmethod
    def validate_rationale_non_empty(cls, value: str) -> str:
        """Require a non-empty rationale after trimming whitespace."""
        if not value.strip():
            raise ValueError("rationale must be non-empty")
        return value

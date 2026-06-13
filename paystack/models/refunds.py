"""Refund Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import PaystackModel


class Refund(PaystackModel):
    id: int | None = None
    integration: int | None = None
    domain: str | None = None
    transaction: int | None = None
    dispute: Any | None = None
    amount: int | None = None
    deducted_amount: Any | None = None
    currency: str | None = None
    channel: str | None = None
    fully_deducted: bool | None = None
    refunded_by: str | None = None
    refunded_at: datetime | None = None
    expected_at: datetime | None = None
    settlement: Any | None = None
    customer_note: str | None = None
    merchant_note: str | None = None
    status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

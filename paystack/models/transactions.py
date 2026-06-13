"""Pydantic models for the Transactions resource."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import Authorization, Customer, Log, PaystackModel, Split


class Transaction(PaystackModel):
    id: int
    domain: str | None = None
    status: str
    reference: str
    receipt_number: str | None = None
    amount: int                          # always in kobo/lowest denomination
    message: str | None = None
    gateway_response: str | None = None
    paid_at: datetime | None = None
    created_at: datetime | None = None
    channel: str | None = None
    currency: str | None = None
    ip_address: str | None = None
    metadata: Any | None = None
    log: Log | None = None
    fees: int | None = None
    fees_split: Any | None = None
    authorization: Authorization | None = None
    customer: Customer | None = None
    plan: Any | None = None
    split: Split | None = None
    order_id: str | None = None
    paidAt: datetime | None = None
    createdAt: datetime | None = None
    requested_amount: int | None = None
    pos_transaction_data: Any | None = None
    source: Any | None = None
    fees_breakdown: Any | None = None
    connect: Any | None = None
    transaction_date: datetime | None = None
    plan_object: Any | None = None
    subaccount: Any | None = None


class TransactionInitData(PaystackModel):
    authorization_url: str
    access_code: str
    reference: str


class TransactionTimeline(PaystackModel):
    time_spent: int | None = None
    attempts: int | None = None
    authentication: Any | None = None
    errors: int | None = None
    success: bool | None = None
    mobile: bool | None = None
    input: list[Any] | None = None
    channel: str | None = None
    history: list[dict[str, Any]] | None = None


class TransactionTotals(PaystackModel):
    total_transactions: int
    total_volume: int
    total_volume_by_currency: list[dict[str, Any]] | None = None
    pending_transfers: int | None = None
    pending_transfers_by_currency: list[dict[str, Any]] | None = None


class TransactionExport(PaystackModel):
    path: str
    expiresAt: str | None = None

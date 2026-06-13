"""Transfer-related Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import PaystackModel


class TransferRecipientDetails(PaystackModel):
    account_number: str | None = None
    account_name: str | None = None
    bank_code: str | None = None
    bank_name: str | None = None


class TransferRecipient(PaystackModel):
    id: int | None = None
    type: str | None = None
    name: str | None = None
    description: str | None = None
    metadata: Any | None = None
    domain: str | None = None
    details: TransferRecipientDetails | None = None
    currency: str | None = None
    recipient_code: str | None = None
    active: bool | None = None
    is_deleted: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Transfer(PaystackModel):
    id: int | None = None
    domain: str | None = None
    amount: int | None = None
    currency: str | None = None
    reference: str | None = None
    source: str | None = None
    source_details: Any | None = None
    reason: str | None = None
    status: str | None = None
    failures: Any | None = None
    transfer_code: str | None = None
    titan_code: Any | None = None
    transferred_at: datetime | None = None
    request: int | None = None
    recipient: TransferRecipient | None = None
    session: Any | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BulkTransferResult(PaystackModel):
    reference: str | None = None
    status: str | None = None


class TransferOTPData(PaystackModel):
    otp: str | None = None
    transfer_code: str | None = None

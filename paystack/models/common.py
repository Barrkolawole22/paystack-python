"""Shared Pydantic models used across multiple Paystack resources."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class PaystackModel(BaseModel):
    """Base model for all Paystack response objects."""

    model_config = ConfigDict(
        extra="allow",          # Forward-compatible: new Paystack fields won't break
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class PaystackResponse(PaystackModel, Generic[DataT]):
    """
    Normalised envelope returned by every SDK method.

    Paystack returns { status, message, data } but shape of `data`
    varies wildly by endpoint. This generic wrapper pins the type.
    """

    status: bool
    message: str
    data: DataT | None = None
    meta: dict[str, Any] | None = None


class PaginatedResponse(PaystackModel, Generic[DataT]):
    """Wrapper for list endpoints that include pagination metadata."""

    status: bool
    message: str
    data: list[DataT] = Field(default_factory=list)
    meta: PaginationMeta | None = None


class PaginationMeta(PaystackModel):
    total: int
    skipped: int
    per_page: int
    page: int
    page_count: int


class Authorization(PaystackModel):
    authorization_code: str
    bin: str | None = None
    last4: str | None = None
    exp_month: str | None = None
    exp_year: str | None = None
    channel: str | None = None
    card_type: str | None = None
    bank: str | None = None
    country_code: str | None = None
    brand: str | None = None
    reusable: bool | None = None
    signature: str | None = None
    account_name: str | None = None


class Customer(PaystackModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    customer_code: str | None = None
    phone: str | None = None
    metadata: dict[str, Any] | None = None
    risk_action: str | None = None
    international_format_phone: str | None = None


class Log(PaystackModel):
    start_time: int | None = None
    time_spent: int | None = None
    attempts: int | None = None
    errors: int | None = None
    success: bool | None = None
    mobile: bool | None = None
    input: list[Any] | None = Field(default_factory=list)
    history: list[dict[str, Any]] | None = Field(default_factory=list)


class Split(PaystackModel):
    id: int | None = None
    name: str | None = None
    type: str | None = None
    currency: str | None = None
    integration: int | None = None
    domain: str | None = None
    split_code: str | None = None
    active: bool | None = None
    bearer_type: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Bank(PaystackModel):
    id: int | None = None
    name: str | None = None
    slug: str | None = None
    code: str | None = None
    longcode: str | None = None
    gateway: str | None = None
    pay_with_bank: bool | None = None
    active: bool | None = None
    country: str | None = None
    currency: str | None = None
    type: str | None = None
    is_deleted: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

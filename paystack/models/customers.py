"""Customer-specific Pydantic models."""

from __future__ import annotations

from typing import Any

from .common import Authorization, Customer


class CustomerDetail(Customer):
    """
    Extended Customer returned by fetch().

    Includes authorization list and subscription history not present
    in the embedded Customer objects returned by transaction endpoints.
    """

    authorizations: list[Authorization] | None = None
    transactions: list[Any] | None = None
    subscriptions: list[Any] | None = None
    identified: bool | None = None
    identifications: Any | None = None
    createdAt: str | None = None
    updatedAt: str | None = None

CustomerFull = CustomerDetail

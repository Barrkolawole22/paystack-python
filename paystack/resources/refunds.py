"""Refunds resource."""

from __future__ import annotations

from typing import Any

from ..base import BaseResource
from ..models.common import PaginatedResponse, PaystackResponse
from ..models.refunds import Refund


class Refunds(BaseResource):
    """
    Manage transaction refunds.

    Reference: https://paystack.com/docs/api/refund/
    """

    def create(
        self,
        *,
        transaction: str,
        amount: int | None = None,
        currency: str | None = None,
        customer_note: str | None = None,
        merchant_note: str | None = None,
    ) -> PaystackResponse[Refund]:
        """Create a refund for a transaction."""
        payload: dict[str, Any] = {"transaction": transaction}
        if amount is not None:
            payload["amount"] = amount
        if currency is not None:
            payload["currency"] = currency
        if customer_note is not None:
            payload["customer_note"] = customer_note
        if merchant_note is not None:
            payload["merchant_note"] = merchant_note

        raw = self._post("/refund", json=payload)
        return PaystackResponse[Refund](
            **{**raw, "data": Refund(**raw["data"])}
        )

    def list(
        self,
        *,
        reference: str | None = None,
        currency: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        per_page: int = 50,
        page: int = 1,
    ) -> PaginatedResponse[Refund]:
        """List refunds."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if reference is not None:
            params["reference"] = reference
        if currency is not None:
            params["currency"] = currency
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date

        raw = self._get("/refund", params=params)
        items = [Refund(**r) for r in raw.get("data", [])]
        return PaginatedResponse[Refund](**{**raw, "data": items})

    def fetch(self, reference: str) -> PaystackResponse[Refund]:
        """Get details of a specific refund."""
        raw = self._get(f"/refund/{reference}")
        return PaystackResponse[Refund](
            **{**raw, "data": Refund(**raw["data"])}
        )

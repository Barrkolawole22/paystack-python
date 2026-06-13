"""Transactions resource."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..base import BaseResource
from ..models.common import PaginatedResponse, PaystackResponse
from ..models.transactions import (
    Transaction,
    TransactionExport,
    TransactionInitData,
    TransactionTimeline,
    TransactionTotals,
)


class Transactions(BaseResource):
    """
    Transactions let you create and manage payments on your integration.

    Reference: https://paystack.com/docs/api/transaction/
    """

    def initialize(
        self,
        *,
        email: str,
        amount: int,
        currency: str = "NGN",
        reference: str | None = None,
        callback_url: str | None = None,
        plan: str | None = None,
        invoice_limit: int | None = None,
        metadata: dict[str, Any] | None = None,
        channels: Sequence[str] | None = None,
        split_code: str | None = None,
        subaccount: str | None = None,
        transaction_charge: int | None = None,
        bearer: str | None = None,
    ) -> PaystackResponse[TransactionInitData]:
        """Initialise a transaction and return an authorization_url."""
        payload: dict[str, Any] = {"email": email, "amount": amount, "currency": currency}
        if reference is not None:
            payload["reference"] = reference
        if callback_url is not None:
            payload["callback_url"] = callback_url
        if plan is not None:
            payload["plan"] = plan
        if invoice_limit is not None:
            payload["invoice_limit"] = invoice_limit
        if metadata is not None:
            payload["metadata"] = metadata
        if channels is not None:
            payload["channels"] = channels
        if split_code is not None:
            payload["split_code"] = split_code
        if subaccount is not None:
            payload["subaccount"] = subaccount
        if transaction_charge is not None:
            payload["transaction_charge"] = transaction_charge
        if bearer is not None:
            payload["bearer"] = bearer

        raw = self._post("/transaction/initialize", json=payload)
        return PaystackResponse[TransactionInitData](
            **{**raw, "data": TransactionInitData(**raw["data"])}
        )

    def verify(self, reference: str) -> PaystackResponse[Transaction]:
        """Confirm the status of a transaction by its reference."""
        raw = self._get(f"/transaction/verify/{reference}")
        return PaystackResponse[Transaction](
            **{**raw, "data": Transaction(**raw["data"])}
        )

    def list(
        self,
        *,
        per_page: int = 50,
        page: int = 1,
        customer: int | None = None,
        status: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        amount: int | None = None,
    ) -> PaginatedResponse[Transaction]:
        """List transactions with optional filters."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if customer is not None:
            params["customer"] = customer
        if status is not None:
            params["status"] = status
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        if amount is not None:
            params["amount"] = amount

        raw = self._get("/transaction", params=params)
        items = [Transaction(**t) for t in raw.get("data", [])]
        return PaginatedResponse[Transaction](**{**raw, "data": items})

    def fetch(self, transaction_id: int) -> PaystackResponse[Transaction]:
        """Get details of a specific transaction by its integer ID."""
        raw = self._get(f"/transaction/{transaction_id}")
        return PaystackResponse[Transaction](
            **{**raw, "data": Transaction(**raw["data"])}
        )

    def charge_authorization(
        self,
        *,
        email: str,
        amount: int,
        authorization_code: str,
        reference: str | None = None,
        currency: str = "NGN",
        metadata: dict[str, Any] | None = None,
        channels: Sequence[str] | None = None,
        subaccount: str | None = None,
        transaction_charge: int | None = None,
        bearer: str | None = None,
        queue: bool = False,
    ) -> PaystackResponse[Transaction]:
        """Charge a reusable authorization code (recurring payments)."""
        payload: dict[str, Any] = {
            "email": email,
            "amount": amount,
            "authorization_code": authorization_code,
            "currency": currency,
            "queue": queue,
        }
        if reference is not None:
            payload["reference"] = reference
        if metadata is not None:
            payload["metadata"] = metadata
        if channels is not None:
            payload["channels"] = channels
        if subaccount is not None:
            payload["subaccount"] = subaccount
        if transaction_charge is not None:
            payload["transaction_charge"] = transaction_charge
        if bearer is not None:
            payload["bearer"] = bearer

        raw = self._post("/transaction/charge_authorization", json=payload)
        return PaystackResponse[Transaction](
            **{**raw, "data": Transaction(**raw["data"])}
        )

    def check_authorization(
        self,
        *,
        email: str,
        amount: int,
        authorization_code: str,
        currency: str = "NGN",
    ) -> PaystackResponse[Transaction]:
        """Validate an authorization without charging the customer."""
        raw = self._post(
            "/transaction/check_authorization",
            json={
                "email": email,
                "amount": amount,
                "authorization_code": authorization_code,
                "currency": currency,
            },
        )
        return PaystackResponse[Transaction](
            **{**raw, "data": Transaction(**raw["data"])}
        )

    def totals(
        self,
        *,
        per_page: int = 50,
        page: int = 1,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> PaystackResponse[TransactionTotals]:
        """Return aggregate transaction volume and pending transfers."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date

        raw = self._get("/transaction/totals", params=params)
        return PaystackResponse[TransactionTotals](
            **{**raw, "data": TransactionTotals(**raw["data"])}
        )

    def export(
        self,
        *,
        per_page: int = 50,
        page: int = 1,
        from_date: str | None = None,
        to_date: str | None = None,
        customer: int | None = None,
        status: str | None = None,
        currency: str | None = None,
        amount: int | None = None,
        settled: bool | None = None,
        settlement: int | None = None,
        payment_page: int | None = None,
    ) -> PaystackResponse[TransactionExport]:
        """Export transactions to CSV. Returns a response with a download path."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        if customer is not None:
            params["customer"] = customer
        if status is not None:
            params["status"] = status
        if currency is not None:
            params["currency"] = currency
        if amount is not None:
            params["amount"] = amount
        if settled is not None:
            params["settled"] = settled
        if settlement is not None:
            params["settlement"] = settlement
        if payment_page is not None:
            params["payment_page"] = payment_page

        raw = self._get("/transaction/export", params=params)
        return PaystackResponse[TransactionExport](
            **{**raw, "data": TransactionExport(**raw["data"])}
        )

    def timeline(
        self, id_or_reference: str | int
    ) -> PaystackResponse[TransactionTimeline]:
        """Get the event timeline for a transaction."""
        raw = self._get(f"/transaction/timeline/{id_or_reference}")
        return PaystackResponse[TransactionTimeline](
            **{**raw, "data": TransactionTimeline(**raw["data"])}
        )

    def partial_debit(
        self,
        *,
        authorization_code: str,
        currency: str,
        amount: int,
        email: str,
        reference: str | None = None,
        at_least: int | None = None,
    ) -> PaystackResponse[Transaction]:
        """Debit a customer for less than the requested amount."""
        payload: dict[str, Any] = {
            "authorization_code": authorization_code,
            "currency": currency,
            "amount": amount,
            "email": email,
        }
        if reference is not None:
            payload["reference"] = reference
        if at_least is not None:
            payload["at_least"] = at_least

        raw = self._post("/transaction/partial_debit", json=payload)
        return PaystackResponse[Transaction](
            **{**raw, "data": Transaction(**raw["data"])}
        )

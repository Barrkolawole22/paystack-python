"""Plans and Subscriptions resources."""

from __future__ import annotations

from typing import Any

from ..base import BaseResource
from ..models.common import PaginatedResponse, PaystackResponse
from ..models.subscriptions import Plan, Subscription, SubscriptionLink


class Plans(BaseResource):
    """
    Manage billing plans for recurring payments.

    Reference: https://paystack.com/docs/api/plan/
    """

    def create(
        self,
        *,
        name: str,
        interval: str,
        amount: int,
        currency: str = "NGN",
        invoice_limit: int | None = None,
        send_invoices: bool = False,
        send_sms: bool = False,
        description: str | None = None,
    ) -> PaystackResponse[Plan]:
        """Create a billing plan."""
        payload: dict[str, Any] = {
            "name": name,
            "interval": interval,
            "amount": amount,
            "currency": currency,
            "send_invoices": send_invoices,
            "send_sms": send_sms,
        }
        if invoice_limit is not None:
            payload["invoice_limit"] = invoice_limit
        if description is not None:
            payload["description"] = description

        raw = self._post("/plan", json=payload)
        return PaystackResponse[Plan](
            **{**raw, "data": Plan(**raw["data"])}
        )

    def list(
        self,
        *,
        per_page: int = 50,
        page: int = 1,
        interval: str | None = None,
        amount: int | None = None,
    ) -> PaginatedResponse[Plan]:
        """List billing plans."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if interval is not None:
            params["interval"] = interval
        if amount is not None:
            params["amount"] = amount

        raw = self._get("/plan", params=params)
        items = [Plan(**p) for p in raw.get("data", [])]
        return PaginatedResponse[Plan](**{**raw, "data": items})

    def fetch(self, id_or_code: str | int) -> PaystackResponse[Plan]:
        """Get details of a billing plan."""
        raw = self._get(f"/plan/{id_or_code}")
        return PaystackResponse[Plan](
            **{**raw, "data": Plan(**raw["data"])}
        )

    def update(
        self,
        id_or_code: str | int,
        *,
        name: str | None = None,
        amount: int | None = None,
        interval: str | None = None,
        description: str | None = None,
        currency: str | None = None,
    ) -> PaystackResponse[None]:
        """Update a billing plan."""
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if amount is not None:
            payload["amount"] = amount
        if interval is not None:
            payload["interval"] = interval
        if description is not None:
            payload["description"] = description
        if currency is not None:
            payload["currency"] = currency

        raw = self._put(f"/plan/{id_or_code}", json=payload)
        return PaystackResponse[None](**raw)


class Subscriptions(BaseResource):
    """
    Manage subscriptions on your integration.

    Reference: https://paystack.com/docs/api/subscription/
    """

    def create(
        self,
        *,
        customer: str,
        plan: str,
        authorization: str | None = None,
        start_date: str | None = None,
    ) -> PaystackResponse[Subscription]:
        """Create a subscription for a customer."""
        payload: dict[str, Any] = {"customer": customer, "plan": plan}
        if authorization is not None:
            payload["authorization"] = authorization
        if start_date is not None:
            payload["start_date"] = start_date

        raw = self._post("/subscription", json=payload)
        return PaystackResponse[Subscription](
            **{**raw, "data": Subscription(**raw["data"])}
        )

    def list(
        self,
        *,
        per_page: int = 50,
        page: int = 1,
        customer: int | None = None,
        plan: int | None = None,
    ) -> PaginatedResponse[Subscription]:
        """List subscriptions."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if customer is not None:
            params["customer"] = customer
        if plan is not None:
            params["plan"] = plan

        raw = self._get("/subscription", params=params)
        items = [Subscription(**s) for s in raw.get("data", [])]
        return PaginatedResponse[Subscription](**{**raw, "data": items})

    def fetch(self, id_or_code: str | int) -> PaystackResponse[Subscription]:
        """Get details of a subscription."""
        raw = self._get(f"/subscription/{id_or_code}")
        return PaystackResponse[Subscription](
            **{**raw, "data": Subscription(**raw["data"])}
        )

    def enable(self, *, code: str, token: str) -> PaystackResponse[None]:
        """Enable a subscription."""
        raw = self._post("/subscription/enable", json={"code": code, "token": token})
        return PaystackResponse[None](**raw)

    def disable(self, *, code: str, token: str) -> PaystackResponse[None]:
        """Disable a subscription."""
        raw = self._post("/subscription/disable", json={"code": code, "token": token})
        return PaystackResponse[None](**raw)

    def generate_update_link(
        self, subscription_code: str
    ) -> PaystackResponse[SubscriptionLink]:
        """Generate a link for the customer to update their subscription."""
        raw = self._get(f"/subscription/{subscription_code}/manage/link")
        return PaystackResponse[SubscriptionLink](
            **{**raw, "data": SubscriptionLink(**raw["data"])}
        )

    def send_update_link(self, subscription_code: str) -> PaystackResponse[None]:
        """Email the subscription update link to the customer."""
        raw = self._post(f"/subscription/{subscription_code}/manage/email")
        return PaystackResponse[None](**raw)

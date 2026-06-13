"""Customers resource."""

from __future__ import annotations

from typing import Any

from ..base import BaseResource
from ..models.common import Customer, PaginatedResponse, PaystackResponse
from ..models.customers import CustomerFull


class Customers(BaseResource):
    """
    Create and manage customers on your integration.

    Reference: https://paystack.com/docs/api/customer/
    """

    def create(
        self,
        *,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PaystackResponse[CustomerFull]:
        """Create a new customer."""
        payload: dict[str, Any] = {"email": email}
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        if phone is not None:
            payload["phone"] = phone
        if metadata is not None:
            payload["metadata"] = metadata

        raw = self._post("/customer", json=payload)
        return PaystackResponse[CustomerFull](
            **{**raw, "data": CustomerFull(**raw["data"])}
        )

    def list(
        self,
        *,
        per_page: int = 50,
        page: int = 1,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> PaginatedResponse[Customer]:
        """List customers."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date

        raw = self._get("/customer", params=params)
        items = [Customer(**c) for c in raw.get("data", [])]
        return PaginatedResponse[Customer](**{**raw, "data": items})

    def fetch(self, email_or_code: str) -> PaystackResponse[CustomerFull]:
        """Get details of a customer by email or customer code."""
        raw = self._get(f"/customer/{email_or_code}")
        return PaystackResponse[CustomerFull](
            **{**raw, "data": CustomerFull(**raw["data"])}
        )

    def update(
        self,
        customer_code: str,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PaystackResponse[CustomerFull]:
        """Update a customer's details."""
        payload: dict[str, Any] = {}
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        if phone is not None:
            payload["phone"] = phone
        if metadata is not None:
            payload["metadata"] = metadata

        raw = self._put(f"/customer/{customer_code}", json=payload)
        return PaystackResponse[CustomerFull](
            **{**raw, "data": CustomerFull(**raw["data"])}
        )

    def validate(
        self,
        customer_code: str,
        *,
        first_name: str,
        last_name: str,
        type: str,
        country: str,
        bvn: str,
        bank_code: str | None = None,
        account_number: str | None = None,
        value: str | None = None,
    ) -> PaystackResponse[None]:
        """Validate a customer's identity."""
        payload: dict[str, Any] = {
            "first_name": first_name,
            "last_name": last_name,
            "type": type,
            "country": country,
            "bvn": bvn,
        }
        if bank_code is not None:
            payload["bank_code"] = bank_code
        if account_number is not None:
            payload["account_number"] = account_number
        if value is not None:
            payload["value"] = value

        raw = self._post(f"/customer/{customer_code}/identification", json=payload)
        return PaystackResponse[None](**raw)

    def whitelist_or_blacklist(
        self, customer: str, risk_action: str
    ) -> PaystackResponse[CustomerFull]:
        """Set a customer's risk action. risk_action: 'allow' or 'deny'."""
        raw = self._post(
            "/customer/set_risk_action",
            json={"customer": customer, "risk_action": risk_action},
        )
        return PaystackResponse[CustomerFull](
            **{**raw, "data": CustomerFull(**raw["data"])}
        )

    def whitelist(self, customer_code: str) -> PaystackResponse[CustomerFull]:
        """Shorthand to set risk action to 'allow'."""
        return self.whitelist_or_blacklist(customer_code, "allow")

    def blacklist(self, customer_code: str) -> PaystackResponse[CustomerFull]:
        """Shorthand to set risk action to 'deny'."""
        return self.whitelist_or_blacklist(customer_code, "deny")

    def deactivate_authorization(
        self, authorization_code: str
    ) -> PaystackResponse[None]:
        """Deactivate a reusable authorization."""
        raw = self._post(
            "/customer/deactivate_authorization",
            json={"authorization_code": authorization_code},
        )
        return PaystackResponse[None](**raw)

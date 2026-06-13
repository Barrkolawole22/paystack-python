"""Identity verification resource."""

from __future__ import annotations

from typing import Any

from ..base import BaseResource
from ..models.common import Bank, PaginatedResponse, PaystackResponse
from ..models.identity import AccountDetails, CardBIN


class Identity(BaseResource):
    """
    Interface to the Paystack Identity / Verification APIs.

    Reference: https://paystack.com/docs/api/verification/
    """

    def resolve_account(
        self, *, account_number: str, bank_code: str
    ) -> PaystackResponse[AccountDetails]:
        """Resolve a bank account number to get the account name."""
        raw = self._get(
            "/bank/resolve",
            params={"account_number": account_number, "bank_code": bank_code},
        )
        return PaystackResponse[AccountDetails](
            **{**raw, "data": AccountDetails(**raw["data"])}
        )

    def validate_account(
        self,
        *,
        account_name: str,
        account_number: str,
        account_type: str,
        bank_code: str,
        country_code: str,
        document_type: str,
        document_number: str | None = None,
    ) -> PaystackResponse[None]:
        """Validate an account by verifying BVN against bank account ownership."""
        payload = {
            "account_name": account_name,
            "account_number": account_number,
            "account_type": account_type,
            "bank_code": bank_code,
            "country_code": country_code,
            "document_type": document_type,
        }
        if document_number is not None:
            payload["document_number"] = document_number

        raw = self._post("/bank/validate", json=payload)
        return PaystackResponse[None](**raw)

    def resolve_card_bin(self, bin: str) -> PaystackResponse[CardBIN]:
        """Get the issuing bank and card brand from a card BIN (first 6 digits)."""
        raw = self._get(f"/decision/bin/{bin}")
        return PaystackResponse[CardBIN](**{**raw, "data": CardBIN(**raw["data"])})

    def list_banks(
        self,
        *,
        country: str = "nigeria",
        use_cursor: bool = False,
        per_page: int = 50,
        pay_with_bank: bool | None = None,
        enabled_for_verification: bool | None = None,
        cursor: str | None = None,
        type: str | None = None,
        currency: str | None = None,
        gateway: str | None = None,
    ) -> PaginatedResponse[Bank]:
        """List all banks supported by Paystack."""
        params = {"country": country, "use_cursor": use_cursor, "perPage": per_page}
        if pay_with_bank is not None:
            params["pay_with_bank"] = pay_with_bank
        if enabled_for_verification is not None:
            params["enabled_for_verification"] = enabled_for_verification
        if cursor is not None:
            params["cursor"] = cursor
        if type is not None:
            params["type"] = type
        if currency is not None:
            params["currency"] = currency
        if gateway is not None:
            params["gateway"] = gateway

        raw = self._get("/bank", params=params)
        items = [Bank(**b) for b in raw.get("data", [])]
        return PaginatedResponse[Bank](**{**raw, "data": items})

    def list_countries(self) -> PaystackResponse[list[Any]]:
        """List countries supported by Paystack."""
        raw = self._get("/country")
        return PaystackResponse[list[Any]](**raw)

    def list_states(self, country: str) -> PaystackResponse[list[Any]]:
        """List states/provinces for a country."""
        raw = self._get("/address_verification/states", params={"country": country})
        return PaystackResponse[list[Any]](**raw)

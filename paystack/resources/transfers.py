"""Transfers resource."""

from __future__ import annotations

from typing import Any

from ..base import BaseResource
from ..models.common import PaginatedResponse, PaystackResponse
from ..models.transfers import BulkTransferResult, Transfer, TransferRecipient


class Transfers(BaseResource):
    """
    Send money to bank accounts and manage transfer recipients.

    Reference: https://paystack.com/docs/api/transfer/
    """

    def initiate(
        self,
        *,
        amount: int,
        recipient: str,
        source: str = "balance",
        reason: str | None = None,
        currency: str = "NGN",
        reference: str | None = None,
    ) -> PaystackResponse[Transfer]:
        """Initiate a transfer to a recipient."""
        payload: dict[str, Any] = {
            "source": source,
            "amount": amount,
            "recipient": recipient,
            "currency": currency,
        }
        if reason is not None:
            payload["reason"] = reason
        if reference is not None:
            payload["reference"] = reference

        raw = self._post("/transfer", json=payload)
        return PaystackResponse[Transfer](
            **{**raw, "data": Transfer(**raw["data"])}
        )

    def finalize(self, *, transfer_code: str, otp: str) -> PaystackResponse[Transfer]:
        """Finalize a transfer that requires OTP confirmation."""
        raw = self._post(
            "/transfer/finalize_transfer",
            json={"transfer_code": transfer_code, "otp": otp},
        )
        return PaystackResponse[Transfer](
            **{**raw, "data": Transfer(**raw["data"])}
        )

    def bulk(
        self,
        *,
        transfers: list[dict[str, Any]],
        source: str = "balance",
    ) -> PaystackResponse[BulkTransferResult]:
        """Initiate multiple transfers in one request."""
        raw = self._post(
            "/transfer/bulk",
            json={"source": source, "transfers": transfers},
        )
        data = BulkTransferResult(**raw["data"]) if raw.get("data") else None
        return PaystackResponse[BulkTransferResult](**{**raw, "data": data})

    def list(
        self,
        *,
        per_page: int = 50,
        page: int = 1,
        customer: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> PaginatedResponse[Transfer]:
        """List transfers."""
        params: dict[str, Any] = {"perPage": per_page, "page": page}
        if customer is not None:
            params["customer"] = customer
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date

        raw = self._get("/transfer", params=params)
        items = [Transfer(**t) for t in raw.get("data", [])]
        return PaginatedResponse[Transfer](**{**raw, "data": items})

    def fetch(self, id_or_code: str | int) -> PaystackResponse[Transfer]:
        """Get details of a specific transfer."""
        raw = self._get(f"/transfer/{id_or_code}")
        return PaystackResponse[Transfer](
            **{**raw, "data": Transfer(**raw["data"])}
        )

    def verify(self, reference: str) -> PaystackResponse[Transfer]:
        """Verify a transfer by its reference."""
        raw = self._get(f"/transfer/verify/{reference}")
        return PaystackResponse[Transfer](
            **{**raw, "data": Transfer(**raw["data"])}
        )

    # ------------------------------------------------------------------ #
    #  Recipients                                                          #
    # ------------------------------------------------------------------ #

    def create_recipient(
        self,
        *,
        type: str,
        name: str,
        account_number: str,
        bank_code: str,
        currency: str = "NGN",
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PaystackResponse[TransferRecipient]:
        """Create a transfer recipient."""
        payload: dict[str, Any] = {
            "type": type,
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": currency,
        }
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata

        raw = self._post("/transferrecipient", json=payload)
        return PaystackResponse[TransferRecipient](
            **{**raw, "data": TransferRecipient(**raw["data"])}
        )

    def list_recipients(
        self, *, per_page: int = 50, page: int = 1
    ) -> PaginatedResponse[TransferRecipient]:
        """List transfer recipients."""
        raw = self._get("/transferrecipient", params={"perPage": per_page, "page": page})
        items = [TransferRecipient(**r) for r in raw.get("data", [])]
        return PaginatedResponse[TransferRecipient](**{**raw, "data": items})

    def fetch_recipient(
        self, id_or_code: str | int
    ) -> PaystackResponse[TransferRecipient]:
        """Get details of a transfer recipient."""
        raw = self._get(f"/transferrecipient/{id_or_code}")
        return PaystackResponse[TransferRecipient](
            **{**raw, "data": TransferRecipient(**raw["data"])}
        )

    def update_recipient(
        self,
        id_or_code: str | int,
        *,
        name: str | None = None,
        email: str | None = None,
    ) -> PaystackResponse[TransferRecipient]:
        """Update a transfer recipient."""
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if email is not None:
            payload["email"] = email

        raw = self._put(f"/transferrecipient/{id_or_code}", json=payload)
        return PaystackResponse[TransferRecipient](
            **{**raw, "data": TransferRecipient(**raw["data"])}
        )

    def delete_recipient(self, id_or_code: str | int) -> PaystackResponse[None]:
        """Delete a transfer recipient."""
        raw = self._delete(f"/transferrecipient/{id_or_code}")
        return PaystackResponse[None](**raw)

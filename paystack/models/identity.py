"""Identity verification Pydantic models."""

from __future__ import annotations

from typing import Any

from .common import PaystackModel


class AccountDetails(PaystackModel):
    account_number: str | None = None
    account_name: str | None = None
    bank_id: int | None = None


class CardBIN(PaystackModel):
    bin: str | None = None
    brand: str | None = None
    sub_brand: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    card_type: str | None = None
    bank: str | None = None
    linked_bank_id: int | None = None


class BVNData(PaystackModel):
    first_name: str | None = None
    last_name: str | None = None
    dob: str | None = None
    formatted_dob: str | None = None
    mobile: str | None = None
    bvn: str | None = None
    is_blacklisted: bool | None = None
    score: Any | None = None

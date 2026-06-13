"""Tests for the Identity resource."""

import pytest
import responses

from paystack import PaystackClient
from paystack.exceptions import InvalidRequestError
from paystack.models.common import Bank
from paystack.models.identity import AccountDetails, CardBIN

BASE_URL = "https://api.paystack.co"
TEST_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def client():
    return PaystackClient(secret_key=TEST_KEY, max_retries=0)


# ── resolve_account ──────────────────────────────────────────────────────────── #

@responses.activate
def test_resolve_account_returns_account_details(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/bank/resolve",
        json={
            "status": True,
            "message": "Account number resolved",
            "data": {
                "account_number": "0123456789",
                "account_name": "Ada Okafor",
                "bank_id": 9,
            },
        },
        status=200,
    )

    resp = client.identity.resolve_account(
        account_number="0123456789", bank_code="058"
    )

    assert resp.status is True
    assert isinstance(resp.data, AccountDetails)
    assert resp.data.account_name == "Ada Okafor"
    assert resp.data.account_number == "0123456789"


@responses.activate
def test_resolve_account_sends_correct_params(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/bank/resolve",
        json={
            "status": True,
            "message": "Account number resolved",
            "data": {"account_number": "0123456789", "account_name": "Ada Okafor", "bank_id": 9},
        },
        status=200,
    )

    client.identity.resolve_account(account_number="0123456789", bank_code="058")

    qs = responses.calls[0].request.url
    assert "account_number=0123456789" in qs
    assert "bank_code=058" in qs


@responses.activate
def test_resolve_account_raises_on_invalid(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/bank/resolve",
        json={"status": False, "message": "Could not resolve account name. Check parameters or try again."},
        status=422,
    )

    from paystack.exceptions import InvalidRequestError

    with pytest.raises(InvalidRequestError):
        client.identity.resolve_account(account_number="0000000000", bank_code="000")


# ── resolve_card_bin ─────────────────────────────────────────────────────────── #

@responses.activate
def test_resolve_card_bin(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/decision/bin/408408",
        json={
            "status": True,
            "message": "Bin resolved",
            "data": {
                "bin": "408408",
                "brand": "Visa",
                "sub_brand": "",
                "country_code": "NG",
                "country_name": "Nigeria",
                "card_type": "DEBIT",
                "bank": "Test Bank",
                "linked_bank_id": 9,
            },
        },
        status=200,
    )

    resp = client.identity.resolve_card_bin("408408")

    assert resp.status is True
    assert isinstance(resp.data, CardBIN)
    assert resp.data.brand == "Visa"
    assert resp.data.country_code == "NG"


# ── list_banks ───────────────────────────────────────────────────────────────── #

@responses.activate
def test_list_banks(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/bank",
        json={
            "status": True,
            "message": "Banks retrieved",
            "data": [
                {"id": 1, "name": "Access Bank", "code": "044", "active": True, "country": "Nigeria", "currency": "NGN"},
                {"id": 2, "name": "GTBank", "code": "058", "active": True, "country": "Nigeria", "currency": "NGN"},
            ],
            "meta": {"total": 2, "skipped": 0, "per_page": 50, "page": 1, "page_count": 1},
        },
        status=200,
    )

    resp = client.identity.list_banks(country="nigeria")

    assert resp.status is True
    assert len(resp.data) == 2
    assert all(isinstance(b, Bank) for b in resp.data)
    assert resp.data[0].code == "044"


# ── validate_account ─────────────────────────────────────────────────────────── #

@responses.activate
def test_validate_account(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/bank/validate",
        json={"status": True, "message": "Personal Account Validation attempted"},
        status=200,
    )

    resp = client.identity.validate_account(
        account_name="Ada Okafor",
        account_number="0123456789",
        account_type="personal",
        bank_code="058",
        country_code="ZA",
        document_type="identityNumber",
        document_number="1234567890123",
    )

    assert resp.status is True

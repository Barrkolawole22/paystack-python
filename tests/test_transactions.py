"""Tests for the Transactions resource."""

import json

import pytest
import responses

from paystack import PaystackClient
from paystack.exceptions import AuthenticationError, NotFoundError, RetryExhaustedError
from paystack.models.transactions import Transaction, TransactionInitData

BASE_URL = "https://api.paystack.co"
TEST_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def client():
    return PaystackClient(secret_key=TEST_KEY, max_retries=2, backoff_factor=0)


# ── initialize ────────────────────────────────────────────────────────────── #

@responses.activate
def test_initialize_returns_authorization_url(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/transaction/initialize",
        json={
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://checkout.paystack.com/abc123",
                "access_code": "abc123",
                "reference": "ref_xyz",
            },
        },
        status=200,
    )

    resp = client.transactions.initialize(email="test@example.com", amount=50_000)

    assert resp.status is True
    assert isinstance(resp.data, TransactionInitData)
    assert resp.data.authorization_url.startswith("https://checkout.paystack.com/")
    assert resp.data.reference == "ref_xyz"


@responses.activate
def test_initialize_sends_correct_payload(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/transaction/initialize",
        json={
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://checkout.paystack.com/x",
                "access_code": "x",
                "reference": "MY_REF",
            },
        },
        status=200,
    )

    client.transactions.initialize(
        email="a@b.com", amount=1000, reference="MY_REF", currency="USD"
    )

    sent = json.loads(responses.calls[0].request.body)
    assert sent["email"] == "a@b.com"
    assert sent["amount"] == 1000
    assert sent["reference"] == "MY_REF"
    assert sent["currency"] == "USD"


# ── verify ────────────────────────────────────────────────────────────────── #

@responses.activate
def test_verify_returns_transaction(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/transaction/verify/ref_123",
        json={
            "status": True,
            "message": "Verification successful",
            "data": {
                "id": 1234567,
                "reference": "ref_123",
                "status": "success",
                "amount": 10000,
                "currency": "NGN",
            },
        },
        status=200,
    )

    resp = client.transactions.verify("ref_123")

    assert resp.status is True
    assert isinstance(resp.data, Transaction)
    assert resp.data.status == "success"
    assert resp.data.amount == 10000


@responses.activate
def test_verify_raises_not_found(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/transaction/verify/bad_ref",
        json={"status": False, "message": "Transaction reference not found"},
        status=404,
    )

    with pytest.raises(NotFoundError) as exc_info:
        client.transactions.verify("bad_ref")

    assert exc_info.value.status_code == 404


# ── list ──────────────────────────────────────────────────────────────────── #

@responses.activate
def test_list_returns_paginated_response(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/transaction",
        json={
            "status": True,
            "message": "Transactions retrieved",
            "data": [
                {"id": 1, "reference": "ref_1", "status": "success", "amount": 5000},
                {"id": 2, "reference": "ref_2", "status": "failed", "amount": 2000},
            ],
            "meta": {"total": 2, "skipped": 0, "per_page": 50, "page": 1, "page_count": 1},
        },
        status=200,
    )

    resp = client.transactions.list(per_page=50, page=1)

    assert resp.status is True
    assert len(resp.data) == 2
    assert all(isinstance(t, Transaction) for t in resp.data)
    assert resp.data[0].reference == "ref_1"


# ── retry logic ───────────────────────────────────────────────────────────── #

@responses.activate
def test_retries_on_500_then_succeeds(client):
    # First call: 500, second call: 200
    responses.add(
        responses.GET,
        f"{BASE_URL}/transaction/verify/ref_retry",
        json={"message": "Internal Server Error"},
        status=500,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/transaction/verify/ref_retry",
        json={
            "status": True,
            "message": "Verification successful",
            "data": {"id": 99, "reference": "ref_retry", "status": "success", "amount": 1000},
        },
        status=200,
    )

    resp = client.transactions.verify("ref_retry")

    assert resp.data.status == "success"
    assert len(responses.calls) == 2


@responses.activate
def test_raises_retry_exhausted_after_max_attempts(client):
    for _ in range(3):   # max_retries=2 means 3 total attempts
        responses.add(
            responses.GET,
            f"{BASE_URL}/transaction/verify/ref_fail",
            json={"message": "Gateway Timeout"},
            status=504,
        )

    with pytest.raises(RetryExhaustedError):
        client.transactions.verify("ref_fail")


# ── authentication ────────────────────────────────────────────────────────── #

@responses.activate
def test_raises_authentication_error_on_401(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/transaction/initialize",
        json={"status": False, "message": "Invalid key"},
        status=401,
    )

    with pytest.raises(AuthenticationError):
        client.transactions.initialize(email="x@x.com", amount=1000)

"""Tests for the Refunds resource."""

import json

import pytest
import responses

from paystack import PaystackClient
from paystack.models.refunds import Refund

BASE_URL = "https://api.paystack.co"
TEST_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def client():
    return PaystackClient(secret_key=TEST_KEY, max_retries=0)


# ── create ───────────────────────────────────────────────────────────────────── #

@responses.activate
def test_create_refund(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/refund",
        json={
            "status": True,
            "message": "Refund created",
            "data": {
                "id": 1,
                "transaction": 987654,
                "amount": 10_000,
                "currency": "NGN",
                "status": "pending",
                "refunded_by": "merchant@example.com",
            },
        },
        status=200,
    )

    resp = client.refunds.create(transaction="987654")

    assert resp.status is True
    assert isinstance(resp.data, Refund)
    assert resp.data.status == "pending"
    assert resp.data.amount == 10_000


@responses.activate
def test_create_refund_sends_correct_payload(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/refund",
        json={
            "status": True,
            "message": "Refund created",
            "data": {"id": 2, "transaction": 111, "amount": 5000, "status": "pending"},
        },
        status=200,
    )

    client.refunds.create(
        transaction="111",
        amount=5000,
        currency="NGN",
        customer_note="Wrong item delivered",
        merchant_note="Verified — issuing refund",
    )

    sent = json.loads(responses.calls[0].request.body)
    assert sent["transaction"] == "111"
    assert sent["amount"] == 5000
    assert sent["currency"] == "NGN"
    assert sent["customer_note"] == "Wrong item delivered"
    assert sent["merchant_note"] == "Verified — issuing refund"


# ── fetch ────────────────────────────────────────────────────────────────────── #

@responses.activate
def test_fetch_refund(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/refund/ref_refund_001",
        json={
            "status": True,
            "message": "Refund retrieved",
            "data": {
                "id": 1,
                "transaction": 987654,
                "amount": 10_000,
                "status": "processed",
                "currency": "NGN",
            },
        },
        status=200,
    )

    resp = client.refunds.fetch("ref_refund_001")

    assert isinstance(resp.data, Refund)
    assert resp.data.status == "processed"


# ── list ─────────────────────────────────────────────────────────────────────── #

@responses.activate
def test_list_refunds(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/refund",
        json={
            "status": True,
            "message": "Refunds retrieved",
            "data": [
                {"id": 1, "transaction": 111, "amount": 5000, "status": "processed"},
                {"id": 2, "transaction": 222, "amount": 2000, "status": "pending"},
            ],
            "meta": {"total": 2, "skipped": 0, "per_page": 50, "page": 1, "page_count": 1},
        },
        status=200,
    )

    resp = client.refunds.list()

    assert resp.status is True
    assert len(resp.data) == 2
    assert all(isinstance(r, Refund) for r in resp.data)
    assert resp.data[0].status == "processed"


@responses.activate
def test_list_refunds_with_filters(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/refund",
        json={
            "status": True,
            "message": "Refunds retrieved",
            "data": [{"id": 1, "transaction": 111, "amount": 5000, "status": "processed"}],
            "meta": {"total": 1, "skipped": 0, "per_page": 10, "page": 1, "page_count": 1},
        },
        status=200,
    )

    client.refunds.list(currency="NGN", per_page=10, page=1)

    qs = responses.calls[0].request.url
    assert "currency=NGN" in qs
    assert "perPage=10" in qs

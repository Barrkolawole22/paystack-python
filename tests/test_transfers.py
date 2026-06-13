"""Tests for the Transfers resource."""

import json

import pytest
import responses

from paystack import PaystackClient
from paystack.models.transfers import Transfer, TransferRecipient

BASE_URL = "https://api.paystack.co"
TEST_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def client():
    return PaystackClient(secret_key=TEST_KEY, max_retries=0)


# ── initiate ────────────────────────────────────────────────────────────────── #

@responses.activate
def test_initiate_returns_transfer(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/transfer",
        json={
            "status": True,
            "message": "Transfer requires OTP to continue",
            "data": {
                "reference": "ref_transfer_001",
                "status": "otp",
                "transfer_code": "TRF_abc123",
                "amount": 500_000,
                "currency": "NGN",
            },
        },
        status=200,
    )

    resp = client.transfers.initiate(amount=500_000, recipient="RCP_xyz")

    assert resp.status is True
    assert isinstance(resp.data, Transfer)
    assert resp.data.transfer_code == "TRF_abc123"
    assert resp.data.amount == 500_000


@responses.activate
def test_initiate_sends_correct_payload(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/transfer",
        json={
            "status": True,
            "message": "Transfer requires OTP to continue",
            "data": {"reference": "MY_REF", "status": "otp", "transfer_code": "TRF_001", "amount": 1000},
        },
        status=200,
    )

    client.transfers.initiate(
        amount=1000, recipient="RCP_abc", reason="Test payment", reference="MY_REF"
    )

    sent = json.loads(responses.calls[0].request.body)
    assert sent["amount"] == 1000
    assert sent["recipient"] == "RCP_abc"
    assert sent["reason"] == "Test payment"
    assert sent["reference"] == "MY_REF"
    assert sent["source"] == "balance"


# ── finalize ─────────────────────────────────────────────────────────────────── #

@responses.activate
def test_finalize_returns_transfer(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/transfer/finalize_transfer",
        json={
            "status": True,
            "message": "Transfer confirmed",
            "data": {
                "transfer_code": "TRF_abc123",
                "status": "success",
                "amount": 500_000,
            },
        },
        status=200,
    )

    resp = client.transfers.finalize(transfer_code="TRF_abc123", otp="123456")

    assert resp.status is True
    assert isinstance(resp.data, Transfer)
    assert resp.data.status == "success"


# ── fetch ────────────────────────────────────────────────────────────────────── #

@responses.activate
def test_fetch_transfer(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/transfer/TRF_abc123",
        json={
            "status": True,
            "message": "Transfer retrieved",
            "data": {
                "transfer_code": "TRF_abc123",
                "status": "success",
                "amount": 500_000,
                "currency": "NGN",
            },
        },
        status=200,
    )

    resp = client.transfers.fetch("TRF_abc123")

    assert isinstance(resp.data, Transfer)
    assert resp.data.transfer_code == "TRF_abc123"


# ── list ─────────────────────────────────────────────────────────────────────── #

@responses.activate
def test_list_returns_paginated_transfers(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/transfer",
        json={
            "status": True,
            "message": "Transfers retrieved",
            "data": [
                {"transfer_code": "TRF_001", "status": "success", "amount": 1000},
                {"transfer_code": "TRF_002", "status": "pending", "amount": 2000},
            ],
            "meta": {"total": 2, "skipped": 0, "per_page": 50, "page": 1, "page_count": 1},
        },
        status=200,
    )

    resp = client.transfers.list(per_page=50, page=1)

    assert resp.status is True
    assert len(resp.data) == 2
    assert all(isinstance(t, Transfer) for t in resp.data)
    assert resp.data[0].transfer_code == "TRF_001"


# ── verify ───────────────────────────────────────────────────────────────────── #

@responses.activate
def test_verify_transfer(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/transfer/verify/ref_transfer_001",
        json={
            "status": True,
            "message": "Transfer retrieved",
            "data": {
                "reference": "ref_transfer_001",
                "status": "success",
                "amount": 500_000,
            },
        },
        status=200,
    )

    resp = client.transfers.verify("ref_transfer_001")

    assert isinstance(resp.data, Transfer)
    assert resp.data.status == "success"


# ── recipients ───────────────────────────────────────────────────────────────── #

@responses.activate
def test_create_recipient(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/transferrecipient",
        json={
            "status": True,
            "message": "Transfer recipient created successfully",
            "data": {
                "recipient_code": "RCP_xyz",
                "name": "Ada Okafor",
                "type": "nuban",
                "currency": "NGN",
                "active": True,
            },
        },
        status=200,
    )

    resp = client.transfers.create_recipient(
        type="nuban",
        name="Ada Okafor",
        account_number="0123456789",
        bank_code="058",
    )

    assert resp.status is True
    assert isinstance(resp.data, TransferRecipient)
    assert resp.data.recipient_code == "RCP_xyz"


@responses.activate
def test_delete_recipient(client):
    responses.add(
        responses.DELETE,
        f"{BASE_URL}/transferrecipient/RCP_xyz",
        json={"status": True, "message": "Transfer recipient set as inactive"},
        status=200,
    )

    resp = client.transfers.delete_recipient("RCP_xyz")

    assert resp.status is True

"""Tests for the Customers resource."""

import pytest
import responses

from paystack import PaystackClient
from paystack.models.customers import CustomerFull

BASE_URL = "https://api.paystack.co"
TEST_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def client():
    return PaystackClient(secret_key=TEST_KEY, max_retries=0)


@responses.activate
def test_create_customer(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/customer",
        json={
            "status": True,
            "message": "Customer created",
            "data": {
                "id": 101,
                "email": "new@example.com",
                "customer_code": "CUS_abc123",
                "first_name": "Ada",
                "last_name": "Okafor",
            },
        },
        status=200,
    )

    resp = client.customers.create(
        email="new@example.com", first_name="Ada", last_name="Okafor"
    )

    assert isinstance(resp.data, CustomerFull)
    assert resp.data.customer_code == "CUS_abc123"
    assert resp.data.email == "new@example.com"


@responses.activate
def test_fetch_customer(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/customer/CUS_abc123",
        json={
            "status": True,
            "message": "Customer retrieved",
            "data": {
                "id": 101,
                "email": "existing@example.com",
                "customer_code": "CUS_abc123",
            },
        },
        status=200,
    )

    resp = client.customers.fetch("CUS_abc123")
    assert resp.data.id == 101


@responses.activate
def test_whitelist_customer(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/customer/set_risk_action",
        json={
            "status": True,
            "message": "Customer updated",
            "data": {
                "id": 101,
                "email": "trusted@example.com",
                "customer_code": "CUS_abc123",
                "risk_action": "allow",
            },
        },
        status=200,
    )

    resp = client.customers.whitelist_or_blacklist(
        customer="CUS_abc123", risk_action="allow"
    )
    assert resp.data.risk_action == "allow"

"""Tests for the Plans and Subscriptions resources."""

import pytest
import responses

from paystack import PaystackClient
from paystack.models.subscriptions import Plan, Subscription, SubscriptionLink

BASE_URL = "https://api.paystack.co"
TEST_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def client():
    return PaystackClient(secret_key=TEST_KEY, max_retries=0)


# ── plans ────────────────────────────────────────────────────────────────────── #

@responses.activate
def test_create_plan(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/plan",
        json={
            "status": True,
            "message": "Plan created",
            "data": {
                "id": 1,
                "name": "Monthly Basic",
                "plan_code": "PLN_abc123",
                "amount": 10_000,
                "interval": "monthly",
                "currency": "NGN",
            },
        },
        status=200,
    )

    resp = client.plans.create(name="Monthly Basic", interval="monthly", amount=10_000)

    assert resp.status is True
    assert isinstance(resp.data, Plan)
    assert resp.data.plan_code == "PLN_abc123"
    assert resp.data.interval == "monthly"


@responses.activate
def test_fetch_plan(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/plan/PLN_abc123",
        json={
            "status": True,
            "message": "Plan retrieved",
            "data": {
                "id": 1,
                "plan_code": "PLN_abc123",
                "name": "Monthly Basic",
                "amount": 10_000,
                "interval": "monthly",
            },
        },
        status=200,
    )

    resp = client.plans.fetch("PLN_abc123")

    assert isinstance(resp.data, Plan)
    assert resp.data.plan_code == "PLN_abc123"


@responses.activate
def test_list_plans(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/plan",
        json={
            "status": True,
            "message": "Plans retrieved",
            "data": [
                {"id": 1, "plan_code": "PLN_001", "name": "Basic", "amount": 5000, "interval": "monthly"},
                {"id": 2, "plan_code": "PLN_002", "name": "Pro", "amount": 15000, "interval": "monthly"},
            ],
            "meta": {"total": 2, "skipped": 0, "per_page": 50, "page": 1, "page_count": 1},
        },
        status=200,
    )

    resp = client.plans.list()

    assert len(resp.data) == 2
    assert all(isinstance(p, Plan) for p in resp.data)


@responses.activate
def test_update_plan(client):
    responses.add(
        responses.PUT,
        f"{BASE_URL}/plan/PLN_abc123",
        json={"status": True, "message": "Plan updated. 1 subscription(s) affected"},
        status=200,
    )

    resp = client.plans.update("PLN_abc123", name="Monthly Basic Plus", amount=12_000)

    assert resp.status is True


# ── subscriptions ────────────────────────────────────────────────────────────── #

@responses.activate
def test_create_subscription(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/subscription",
        json={
            "status": True,
            "message": "Subscription successfully created",
            "data": {
                "id": 10,
                "subscription_code": "SUB_abc123",
                "status": "active",
                "amount": 10_000,
                "email_token": "tok_xyz",
            },
        },
        status=200,
    )

    resp = client.subscriptions.create(customer="CUS_abc", plan="PLN_abc123")

    assert resp.status is True
    assert isinstance(resp.data, Subscription)
    assert resp.data.subscription_code == "SUB_abc123"
    assert resp.data.status == "active"


@responses.activate
def test_fetch_subscription(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/subscription/SUB_abc123",
        json={
            "status": True,
            "message": "Subscription retrieved successfully",
            "data": {
                "id": 10,
                "subscription_code": "SUB_abc123",
                "status": "active",
                "amount": 10_000,
            },
        },
        status=200,
    )

    resp = client.subscriptions.fetch("SUB_abc123")

    assert isinstance(resp.data, Subscription)
    assert resp.data.subscription_code == "SUB_abc123"


@responses.activate
def test_enable_subscription(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/subscription/enable",
        json={"status": True, "message": "Subscription enabled successfully"},
        status=200,
    )

    resp = client.subscriptions.enable(code="SUB_abc123", token="tok_xyz")

    assert resp.status is True


@responses.activate
def test_disable_subscription(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/subscription/disable",
        json={"status": True, "message": "Subscription disabled successfully"},
        status=200,
    )

    resp = client.subscriptions.disable(code="SUB_abc123", token="tok_xyz")

    assert resp.status is True


@responses.activate
def test_generate_update_link(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/subscription/SUB_abc123/manage/link",
        json={
            "status": True,
            "message": "Link generated",
            "data": {"link": "https://paystack.com/manage/SUB_abc123"},
        },
        status=200,
    )

    resp = client.subscriptions.generate_update_link("SUB_abc123")

    assert isinstance(resp.data, SubscriptionLink)
    assert resp.data.link.startswith("https://")

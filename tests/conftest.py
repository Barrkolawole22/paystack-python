"""Shared pytest fixtures."""

import pytest

from paystack import PaystackClient

TEST_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def client() -> PaystackClient:
    """Default test client — no retries, instant backoff."""
    return PaystackClient(secret_key=TEST_KEY, max_retries=0, backoff_factor=0)

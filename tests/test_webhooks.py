"""Tests for webhook signature verification."""

import hashlib
import hmac
import json

import pytest

from paystack.exceptions import WebhookSignatureError
from paystack.webhooks import WebhookEvent, parse_event, verify_signature

SECRET = "sk_test_webhooksecret"


def _sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha512).hexdigest()


def test_verify_signature_valid():
    payload = b'{"event": "charge.success", "data": {"amount": 10000}}'
    sig = _sign(payload, SECRET)
    assert verify_signature(payload, sig, SECRET) is True


def test_verify_signature_invalid_raises():
    payload = b'{"event": "charge.success"}'
    with pytest.raises(WebhookSignatureError):
        verify_signature(payload, "bad_signature", SECRET)


def test_parse_event_returns_dict():
    payload = json.dumps({"event": "charge.success", "data": {"id": 1}}).encode()
    result = parse_event(payload)
    assert result["event"] == "charge.success"


def test_webhook_event_type():
    payload = json.dumps({"event": "transfer.success", "data": {"amount": 5000}}).encode()
    sig = _sign(payload, SECRET)
    event = WebhookEvent(payload, sig, SECRET)
    assert event.type == "transfer.success"
    assert event.data["amount"] == 5000


def test_webhook_event_skips_verification():
    payload = json.dumps({"event": "charge.failed", "data": {}}).encode()
    # No signature provided — should not raise when verify=False
    event = WebhookEvent(payload, "", SECRET, verify=False)
    assert event.type == "charge.failed"

"""
Webhook signature verification and event parsing.

Paystack signs every webhook payload with your secret key using HMAC-SHA512.
Always verify the signature before processing events in production.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, cast

from .exceptions import WebhookSignatureError


def verify_signature(payload: bytes, signature: str, secret_key: str) -> bool:
    """
    Verify that a webhook payload was signed by Paystack.

    Parameters
    ----------
    payload:
        The raw request body bytes (do **not** decode first).
    signature:
        The ``X-Paystack-Signature`` header value.
    secret_key:
        Your Paystack secret key.

    Returns
    -------
    bool
        ``True`` if the signature is valid.

    Raises
    ------
    WebhookSignatureError
        If the signature does not match.

    Example
    -------
    .. code-block:: python

        # Django view
        from paystack.webhooks import verify_signature

        def paystack_webhook(request):
            sig = request.headers.get("X-Paystack-Signature", "")
            try:
                verify_signature(request.body, sig, settings.PAYSTACK_SECRET_KEY)
            except WebhookSignatureError:
                return HttpResponse(status=400)

            event = json.loads(request.body)
            handle_event(event)
            return HttpResponse(status=200)
    """
    expected = hmac.new(
        secret_key.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise WebhookSignatureError(
            "Webhook signature verification failed. "
            "Ensure you are using the correct secret key and the raw request body."
        )

    return True


def parse_event(payload: bytes | str) -> dict[str, Any]:
    """
    Parse a webhook payload into a Python dict.

    Parameters
    ----------
    payload:
        Raw request body (bytes or str).
    """
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    return cast(dict[str, Any], json.loads(payload))


class WebhookEvent:
    """
    Typed wrapper around a Paystack webhook event.

    Usage
    -----
    .. code-block:: python

        event = WebhookEvent(raw_body, headers["X-Paystack-Signature"], secret_key)
        if event.type == "charge.success":
            process_payment(event.data)
    """

    def __init__(
        self,
        payload: bytes,
        signature: str,
        secret_key: str,
        *,
        verify: bool = True,
    ) -> None:
        if verify:
            verify_signature(payload, signature, secret_key)
        self._data = parse_event(payload)

    @property
    def type(self) -> str:
        """The event type, e.g. ``"charge.success"``."""
        return cast(str, self._data.get("event", ""))

    @property
    def data(self) -> dict[str, Any]:
        """The event payload data."""
        return cast(dict[str, Any], self._data.get("data", {}))

    @property
    def raw(self) -> dict[str, Any]:
        """The full raw event dict."""
        return self._data

    def __repr__(self) -> str:
        return f"WebhookEvent(type={self.type!r})"

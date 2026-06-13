"""
PaystackClient — the single entry point to the SDK.

Usage
-----
.. code-block:: python

    from paystack import PaystackClient

    paystack = PaystackClient(secret_key="sk_test_...")

    # Initialise a payment
    response = paystack.transactions.initialize(
        email="customer@example.com",
        amount=50_000,   # NGN 500.00
    )
    print(response.data.authorization_url)

    # Verify a payment
    result = paystack.transactions.verify("txn_ref_abc123")
    if result.data.status == "success":
        fulfil_order()
"""

from __future__ import annotations

import logging
import os

import requests

from .resources.customers import Customers
from .resources.identity import Identity
from .resources.refunds import Refunds
from .resources.subscriptions import Plans, Subscriptions
from .resources.transactions import Transactions
from .resources.transfers import Transfers

log = logging.getLogger("paystack")


class PaystackClient:
    """
    Unified client for the Paystack API.

    All resource interfaces are exposed as attributes on this class so your
    IDE autocomplete works out of the box.

    Parameters
    ----------
    secret_key:
        Your Paystack secret key. If omitted, the value of the
        ``PAYSTACK_SECRET_KEY`` environment variable is used.
    timeout:
        HTTP request timeout in seconds. Default 30.
    max_retries:
        Number of times to retry failed requests before raising. Default 3.
    backoff_factor:
        Multiplier applied to the exponential backoff delay. Default 0.5.
    session:
        Supply a custom ``requests.Session`` (useful in tests).

    Raises
    ------
    ValueError
        If no secret key is provided and ``PAYSTACK_SECRET_KEY`` is not set.
    """

    def __init__(
        self,
        secret_key: str | None = None,
        *,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        session: requests.Session | None = None,
    ) -> None:
        resolved_key = secret_key or os.environ.get("PAYSTACK_SECRET_KEY")
        if not resolved_key:
            raise ValueError(
                "A Paystack secret key is required. Pass `secret_key=` or set "
                "the PAYSTACK_SECRET_KEY environment variable."
            )

        self.transactions = Transactions(
            resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            session=session,
        )
        self.customers = Customers(
            resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            session=session,
        )
        self.transfers = Transfers(
            resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            session=session,
        )
        self.plans = Plans(
            resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            session=session,
        )
        self.subscriptions = Subscriptions(
            resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            session=session,
        )
        self.refunds = Refunds(
            resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            session=session,
        )
        self.identity = Identity(
            resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            session=session,
        )

    def __repr__(self) -> str:
        mode = "live" if self.transactions._secret_key.startswith("sk_live_") else "test"
        return f"PaystackClient(mode={mode!r})"

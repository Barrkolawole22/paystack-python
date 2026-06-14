# paystack-python

A clean, fully-typed Python SDK for the [Paystack](https://paystack.com) API — full surface coverage, Pydantic v2 models, and automatic retry logic.

[![PyPI version](https://img.shields.io/pypi/v/paystack-sdk-python.svg)](https://pypi.org/project/paystack-sdk-python/)
[![Python versions](https://img.shields.io/pypi/pyversions/paystack-sdk-python.svg)](https://pypi.org/project/paystack-sdk-python/)
[![Tests](https://github.com/Barrkolawole22/paystack-python/actions/workflows/publish.yml/badge.svg)](https://github.com/Barrkolawole22/paystack-python/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why this exists

This started as a project to design and ship a typed Python API client end-to-end: a shared HTTP layer with automatic retry/backoff and structured exceptions, Pydantic v2 models for every response shape, full `mypy --strict` coverage, a mocked test suite, and a CI/CD pipeline that publishes to PyPI on tag.

Paystack's API was the target because it's a real, well-documented payments API with a wide, varied surface — transactions, transfers, subscriptions, refunds, identity verification, webhooks — enough breadth to exercise the architecture properly.

---

## Installation

```bash
pip install paystack-sdk-python
```

---

## Quick start

```python
from paystack import PaystackClient

paystack = PaystackClient(secret_key="sk_test_...")

# Or use an environment variable: PAYSTACK_SECRET_KEY
paystack = PaystackClient()

# Initialise a payment — returns a typed Pydantic model
response = paystack.transactions.initialize(
    email="customer@example.com",
    amount=50_000,   # ₦500.00 — always in lowest denomination (kobo)
)
print(response.data.authorization_url)   # redirect the user here

# Verify after payment
result = paystack.transactions.verify("txn_reference_xyz")
if result.data.status == "success":
    fulfil_order()
```

---

## API coverage

| Resource | Operations |
|---|---|
| **Transactions** | initialize, verify, list, fetch, charge_authorization, check_authorization, timeline, totals, export, partial_debit |
| **Customers** | create, list, fetch, update, validate, whitelist/blacklist, deactivate_authorization |
| **Transfers** | create_recipient, list/fetch/update/delete recipient, initiate, bulk, finalize, verify, fetch, list |
| **Plans** | create, list, fetch, update |
| **Subscriptions** | create, list, fetch, enable, disable, generate_update_link, send_update_link |
| **Refunds** | create, list, fetch |
| **Identity** | resolve_account, validate_account, resolve_card_bin, list_banks, list_countries, list_states |
| **Webhooks** | verify_signature, parse_event, WebhookEvent |

---

## Key features

### Typed responses everywhere

Every method returns a `PaystackResponse[T]` or `PaginatedResponse[T]`. Your editor knows the exact shape of `response.data` before you run a single line.

```python
resp = paystack.transactions.verify("ref_123")
# resp.data is Transaction — fully typed
print(resp.data.amount)          # int (kobo)
print(resp.data.authorization)   # Authorization | None
```

### Automatic retry with exponential backoff

Transient failures (429, 5xx) are retried automatically. Configure per-client:

```python
paystack = PaystackClient(
    secret_key="sk_...",
    max_retries=3,       # default
    backoff_factor=0.5,  # waits: 0s, 1s, 2s between attempts
)
```

### Normalisation layer

Paystack returns different response shapes across endpoints. Every response is normalised into a consistent `PaystackResponse[T]` envelope — no more `response["data"]["authorization_url"]` guesswork.

### Webhook verification

```python
from paystack.webhooks import WebhookEvent
from paystack.exceptions import WebhookSignatureError

# Django/Flask/FastAPI view
def webhook(request):
    try:
        event = WebhookEvent(
            payload=request.body,
            signature=request.headers["X-Paystack-Signature"],
            secret_key=settings.PAYSTACK_SECRET_KEY,
        )
    except WebhookSignatureError:
        return HttpResponse(status=400)

    if event.type == "charge.success":
        process_payment(event.data)
    elif event.type == "transfer.success":
        confirm_transfer(event.data)

    return HttpResponse(status=200)
```

---

## Advanced usage

### Transfers

```python
# 1. Create a recipient
recipient = paystack.transfers.create_recipient(
    type="nuban",
    name="Ada Okafor",
    account_number="0123456789",
    bank_code="058",   # GTBank
)

# 2. Initiate the transfer
transfer = paystack.transfers.initiate(
    amount=250_000,   # ₦2,500
    recipient=recipient.data.recipient_code,
    reason="Freelance payment - Invoice #42",
)

# 3. Verify later
result = paystack.transfers.verify(transfer.data.transfer_code)
```

### Subscriptions

```python
# Create a monthly plan
plan = paystack.plans.create(
    name="Pro Monthly",
    amount=2_000_000,   # ₦20,000/month
    interval="monthly",
)

# Subscribe a customer
sub = paystack.subscriptions.create(
    customer="CUS_xxxxx",
    plan=plan.data.plan_code,
)

# Disable when they cancel
paystack.subscriptions.disable(
    code=sub.data.subscription_code,
    token=sub.data.email_token,
)
```

### Identity verification

```python
# Resolve a bank account before sending money
account = paystack.identity.resolve_account(
    account_number="0123456789",
    bank_code="058",
)
print(f"Sending to: {account.data.account_name}")

# List all banks
banks = paystack.identity.list_banks(country="nigeria")
```

---

## Error handling

```python
from paystack.exceptions import (
    AuthenticationError,
    InvalidRequestError,
    NotFoundError,
    PaystackError,
    RateLimitError,
    RetryExhaustedError,
    ServerError,
)

try:
    result = paystack.transactions.verify("ref_xyz")
except NotFoundError:
    print("Transaction not found")
except AuthenticationError:
    print("Check your secret key")
except RetryExhaustedError as e:
    print(f"Failed after retries: {e.status_code}")
except PaystackError as e:
    print(f"Unexpected error: {e.message} (HTTP {e.status_code})")
```

---

## Development

```bash
git clone https://github.com/Barrkolawole22/paystack-python
cd paystack-python
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=paystack --cov-report=term-missing

# Lint
ruff check paystack/

# Type check
mypy paystack/
```

---

## Contributing

PRs are welcome! Please open an issue first to discuss what you'd like to change.

Areas where contributions are especially valued:
- Additional Paystack resources (Disputes, Settlements, Charges, Bulk Charges, Payment Pages)
- Async client (`httpx`-based `AsyncPaystackClient`)
- Django integration helpers

---

## License

MIT © 2026

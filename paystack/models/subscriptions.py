"""Subscription and Plan Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import PaystackModel


class Plan(PaystackModel):
    id: int | None = None
    name: str | None = None
    plan_code: str | None = None
    description: str | None = None
    amount: int | None = None
    interval: str | None = None
    currency: str | None = None
    send_invoices: bool | None = None
    send_sms: bool | None = None
    hosted_page: bool | None = None
    hosted_page_url: str | None = None
    hosted_page_summary: str | None = None
    integration: int | None = None
    domain: str | None = None
    migrate: Any | None = None
    is_deleted: bool | None = None
    is_archived: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SubscriptionLink(PaystackModel):
    link: str | None = None


class ManageSubscriptionLink(PaystackModel):
    link: str | None = None


class Subscription(PaystackModel):
    id: int | None = None
    domain: str | None = None
    status: str | None = None
    subscription_code: str | None = None
    email_token: str | None = None
    amount: int | None = None
    cron_expression: str | None = None
    next_payment_date: datetime | None = None
    open_invoice: Any | None = None
    integration: int | None = None
    plan: Plan | None = None
    authorization: Any | None = None
    customer: Any | None = None
    invoice_limit: int | None = None
    most_recent_invoice: Any | None = None
    cancelledAt: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

"""
Base HTTP client with automatic retry and exponential backoff.

All resource classes inherit from BaseResource and share a single
requests.Session for connection pooling.
"""

from __future__ import annotations

import logging
import time
from typing import Any, cast
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import HTTP_EXCEPTION_MAP, PaystackError, RetryExhaustedError

log = logging.getLogger("paystack")

BASE_URL = "https://api.paystack.co/"
DEFAULT_TIMEOUT = 30          # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 0.5    # wait: 0s, 1s, 2s, ...
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _build_session(max_retries: int, backoff: float) -> requests.Session:
    """
    Build a requests.Session with connection-level retry (network errors only).
    Application-level retries (4xx/5xx) are handled in _request().
    """
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=backoff,
        status_forcelist=set(),        # we handle status retries ourselves
        raise_on_status=False,
        allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class BaseResource:
    """
    Shared HTTP layer for every Paystack resource.

    Parameters
    ----------
    secret_key:
        Your Paystack secret key (sk_live_... or sk_test_...).
    timeout:
        Request timeout in seconds.
    max_retries:
        How many times to retry retryable failures before raising.
    backoff_factor:
        Multiplier for exponential backoff between retries.
    session:
        Optionally pass a pre-built requests.Session (useful for testing).
    """

    def __init__(
        self,
        secret_key: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = RETRY_BACKOFF_FACTOR,
        session: requests.Session | None = None,
    ) -> None:
        self._secret_key = secret_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._session = session or _build_session(max_retries, backoff_factor)
        self._session.headers.update(
            {
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "paystack-python/1.0.0",
            }
        )

    # ------------------------------------------------------------------ #
    #  Internal HTTP helpers                                               #
    # ------------------------------------------------------------------ #

    def _url(self, path: str) -> str:
        return urljoin(BASE_URL, path.lstrip("/"))

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an HTTP request with automatic retry + exponential backoff.

        Retries are attempted for:
          - HTTP 429 (rate limit)
          - HTTP 5xx (server errors)

        All other error responses raise immediately.
        """
        url = self._url(path)
        attempt = 0

        while True:
            attempt += 1
            log.debug("%s %s (attempt %d)", method.upper(), url, attempt)

            try:
                response = self._session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json,
                    timeout=self._timeout,
                )
            except requests.exceptions.ConnectionError as exc:
                raise PaystackError(f"Connection error: {exc}") from exc
            except requests.exceptions.Timeout as exc:
                raise PaystackError(f"Request timed out after {self._timeout}s") from exc

            status = response.status_code

            # -- success ---------------------------------------------------- #
            if 200 <= status < 300:
                try:
                    return cast(dict[str, Any], response.json())
                except ValueError as exc:
                    raise PaystackError("Invalid JSON in Paystack response") from exc

            # -- retryable failure --------------------------------------------#
            if status in RETRYABLE_STATUS_CODES and attempt <= self._max_retries:
                wait = self._backoff_factor * (2 ** (attempt - 1))
                log.warning(
                    "Paystack returned %d; retrying in %.1fs (attempt %d/%d)",
                    status, wait, attempt, self._max_retries,
                )
                time.sleep(wait)
                continue

            # -- terminal failure ----------------------------------------------#
            if attempt > self._max_retries and status in RETRYABLE_STATUS_CODES:
                raise RetryExhaustedError(
                    f"Failed after {self._max_retries} retries (last status: {status})",
                    status_code=status,
                )

            try:
                body = response.json()
                message = body.get("message", response.text)
            except ValueError:
                message = response.text

            exc_class = HTTP_EXCEPTION_MAP.get(status, PaystackError)
            raise exc_class(message, status_code=status, response=response)

    # ------------------------------------------------------------------ #
    #  Public HTTP verb shortcuts                                          #
    # ------------------------------------------------------------------ #

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("GET", path, params=params)

    def _post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("POST", path, json=json)

    def _put(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("PUT", path, json=json)

    def _delete(self, path: str) -> dict[str, Any]:
        return self._request("DELETE", path)

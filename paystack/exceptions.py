"""Custom exceptions for the Paystack Python SDK."""

from typing import Any


class PaystackError(Exception):
    """Base exception for all Paystack SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"status_code={self.status_code})"
        )


class AuthenticationError(PaystackError):
    """Raised when the API key is invalid or missing."""
    pass


class InvalidRequestError(PaystackError):
    """Raised when the request is malformed or contains invalid parameters."""
    pass


class NotFoundError(PaystackError):
    """Raised when the requested resource does not exist."""
    pass


class RateLimitError(PaystackError):
    """Raised when Paystack's rate limit is exceeded."""
    pass


class ServerError(PaystackError):
    """Raised when Paystack returns a 5xx error."""
    pass


class RetryExhaustedError(PaystackError):
    """Raised when all retry attempts have been exhausted."""
    pass


class WebhookSignatureError(PaystackError):
    """Raised when webhook signature verification fails."""
    pass


# HTTP status code → exception class mapping
HTTP_EXCEPTION_MAP: dict[int, type[PaystackError]] = {
    401: AuthenticationError,
    400: InvalidRequestError,
    404: NotFoundError,
    422: InvalidRequestError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}

"""Custom exception types for the liquipydia library."""


class LiquipediaError(Exception):
    """Base exception for all liquipydia errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AuthError(LiquipediaError):
    """Raised when the API key is invalid or missing (HTTP 403)."""


class NotFoundError(LiquipediaError):
    """Raised when the requested data does not exist (HTTP 404)."""


class RateLimitError(LiquipediaError):
    """Raised when the API rate limit is exceeded (HTTP 429).

    Attributes:
        retry_after: Suggested wait time in seconds before retrying, or None if unknown.
    """

    def __init__(self, message: str, *, retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        super().__init__(message)


class ApiError(LiquipediaError):
    """Raised when the API returns an error in the response body."""

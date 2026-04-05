"""Tests for the liquipydia exception hierarchy."""

from liquipydia import ApiError, AuthError, LiquipediaError, NotFoundError, RateLimitError


def test_liquipedia_error_is_exception() -> None:
    """Verify that LiquipediaError inherits from Exception."""
    assert issubclass(LiquipediaError, Exception)


def test_liquipedia_error_message() -> None:
    """Verify that LiquipediaError stores its message."""
    err = LiquipediaError("something went wrong")
    assert err.message == "something went wrong"
    assert str(err) == "something went wrong"


def test_auth_error_is_liquipedia_error() -> None:
    """Verify that AuthError is a subclass of LiquipediaError."""
    assert issubclass(AuthError, LiquipediaError)


def test_not_found_error_is_liquipedia_error() -> None:
    """Verify that NotFoundError is a subclass of LiquipediaError."""
    assert issubclass(NotFoundError, LiquipediaError)


def test_rate_limit_error_is_liquipedia_error() -> None:
    """Verify that RateLimitError is a subclass of LiquipediaError."""
    assert issubclass(RateLimitError, LiquipediaError)


def test_rate_limit_error_retry_after() -> None:
    """Verify that RateLimitError carries retry_after."""
    err = RateLimitError("too many requests", retry_after=30)
    assert err.retry_after == 30
    assert err.message == "too many requests"


def test_rate_limit_error_retry_after_default() -> None:
    """Verify that RateLimitError defaults retry_after to None."""
    err = RateLimitError("too many requests")
    assert err.retry_after is None


def test_api_error_is_liquipedia_error() -> None:
    """Verify that ApiError is a subclass of LiquipediaError."""
    assert issubclass(ApiError, LiquipediaError)

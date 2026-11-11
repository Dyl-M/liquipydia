"""Tests for the liquipydia exception hierarchy."""

# Third-party
import pytest

# Local
from liquipydia import ApiError, AuthError, LiquipediaError, NetworkError, NotFoundError, RateLimitError


def test_liquipedia_error_is_exception() -> None:
    """Verify that LiquipediaError inherits from Exception."""
    assert issubclass(LiquipediaError, Exception)


def test_liquipedia_error_message() -> None:
    """Verify that LiquipediaError stores its message."""
    err = LiquipediaError("something went wrong")
    assert err.message == "something went wrong"
    assert str(err) == "something went wrong"


@pytest.mark.parametrize(
    "error_cls",
    [AuthError, NotFoundError, RateLimitError, ApiError, NetworkError],
    ids=lambda cls: cls.__name__,
)
def test_is_liquipedia_error(error_cls: type[Exception]) -> None:
    """Verify that every specific error is a subclass of LiquipediaError, so one except clause catches them all."""
    assert issubclass(error_cls, LiquipediaError)


def test_rate_limit_error_retry_after() -> None:
    """Verify that RateLimitError carries retry_after."""
    err = RateLimitError("too many requests", retry_after=30)
    assert err.retry_after == 30
    assert err.message == "too many requests"


def test_rate_limit_error_retry_after_default() -> None:
    """Verify that RateLimitError defaults retry_after to None."""
    err = RateLimitError("too many requests")
    assert err.retry_after is None

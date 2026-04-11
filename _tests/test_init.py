"""Tests for the liquipydia package initialization."""

from liquipydia import __author__, __version__


def test_version_is_string() -> None:
    """Verify that __version__ is a string."""
    assert isinstance(__version__, str)


def test_version_value() -> None:
    """Verify that __version__ matches the expected value."""
    assert __version__ == "0.1.0"


def test_author() -> None:
    """Verify that __author__ matches the expected value."""
    assert __author__ == "Dylan Monfret"

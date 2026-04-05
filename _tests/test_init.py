"""Tests for the liquipydia package initialization."""

from liquipydia import __author__, __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)


def test_version_value() -> None:
    assert __version__ == "0.0.1"


def test_author() -> None:
    assert __author__ == "Dylan Monfret"

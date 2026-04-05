"""Tests for the ApiResponse dataclass."""

from liquipydia import ApiResponse


def test_api_response_stores_result() -> None:
    """Verify that ApiResponse stores the result list."""
    resp = ApiResponse(result=[{"id": 1}], warnings=[])
    assert resp.result == [{"id": 1}]


def test_api_response_stores_warnings() -> None:
    """Verify that ApiResponse stores warnings."""
    resp = ApiResponse(result=[], warnings=["deprecated field"])
    assert resp.warnings == ["deprecated field"]


def test_api_response_empty_defaults() -> None:
    """Verify that ApiResponse works with empty lists."""
    resp = ApiResponse(result=[], warnings=[])
    assert resp.result == []
    assert resp.warnings == []


def test_api_response_is_frozen() -> None:
    """Verify that ApiResponse is immutable."""
    import pytest

    resp = ApiResponse(result=[], warnings=[])
    with pytest.raises(AttributeError):
        # noinspection PyDataclass
        resp.result = [{"id": 1}]  # type: ignore[misc]

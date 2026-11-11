"""Shared helpers for the unit test modules."""

# Standard library
from urllib.parse import parse_qs

# Third-party
import httpx

# Local
from liquipydia import LiquipediaClient

BASE_URL = "https://api.liquipedia.net/api/v3/"


def make_client(**kwargs: object) -> LiquipediaClient:
    """Create a client with defaults suitable for testing."""
    defaults: dict[str, object] = {"app_name": "test-app", "api_key": "test-key", "timeout": 5.0}
    defaults.update(kwargs)
    return LiquipediaClient(**defaults)  # type: ignore[arg-type]


def get_query_params(request: httpx.Request) -> dict[str, str]:
    """Extract query parameters from a request as a flat dict."""
    parsed = parse_qs(str(request.url.params))
    return {k: v[0] for k, v in parsed.items()}

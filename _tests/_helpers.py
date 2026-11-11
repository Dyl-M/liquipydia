"""Shared helpers for the unit test modules."""

# Standard library
from typing import Any
from urllib.parse import parse_qs

# Third-party
import httpx

# Local
from liquipydia import LiquipediaClient

API_PATH = "/api/v3/"


def make_client(**kwargs: Any) -> LiquipediaClient:
    """Create a client with defaults suitable for testing."""
    defaults: dict[str, Any] = {"app_name": "test-app", "api_key": "test-key", "timeout": 5.0}
    defaults.update(kwargs)
    return LiquipediaClient(**defaults)


def get_query_params(request: httpx.Request) -> dict[str, str]:
    """Extract query parameters from a request as a flat dict."""
    parsed = parse_qs(str(request.url.params))
    return {k: v[0] for k, v in parsed.items()}


class MockApi:
    """A scripted stand-in for the LPDB API, plugged into a client through its ``transport`` keyword.

    Each request gets the next outcome (the last one repeats once they run out): a response is served as a fresh copy,
    an exception is raised. Every request is recorded in :attr:`requests`.

    Args:
        *outcomes: Responses or exceptions, in order; an empty ``200`` page when none are given.
    """

    def __init__(self, *outcomes: httpx.Response | Exception) -> None:
        """Script the outcomes served to successive requests."""
        self._outcomes = outcomes or (httpx.Response(200, json={"result": []}),)
        self.requests: list[httpx.Request] = []

    @property
    def transport(self) -> httpx.MockTransport:
        """A transport serving the scripted outcomes, for clients built by hand."""
        return httpx.MockTransport(self._handle)

    @property
    def last_request(self) -> httpx.Request:
        """The most recent request received."""
        return self.requests[-1]

    def client(self, **kwargs: Any) -> LiquipediaClient:
        """Create a test client (see :func:`make_client`) whose requests this mock answers."""
        return make_client(transport=self.transport, **kwargs)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        """Record the request and answer it with the next scripted outcome."""
        self.requests.append(request)
        outcome = self._outcomes[min(len(self.requests), len(self._outcomes)) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return httpx.Response(outcome.status_code, headers=outcome.headers, content=outcome.content)

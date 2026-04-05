"""Tests for the liquipydia core client."""

import httpx
import pytest
import respx

from liquipydia import (
    ApiError,
    AuthError,
    LiquipediaClient,
    LiquipediaError,
    NotFoundError,
    RateLimitError,
    __version__,
)

BASE_URL = "https://api.liquipedia.net/api/v3/"

# === Helpers ===


def _make_client(**kwargs: object) -> LiquipediaClient:
    """Create a client with defaults suitable for testing."""
    defaults: dict[str, object] = {"app_name": "test-app", "api_key": "test-key", "timeout": 5.0}
    defaults.update(kwargs)
    return LiquipediaClient(**defaults)  # type: ignore[arg-type]


# === Constructor & Headers ===


class TestConstructor:
    """Tests for LiquipediaClient construction and header setup."""

    @respx.mock
    def test_user_agent_header(self) -> None:
        """Verify User-Agent header is set correctly."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client(app_name="my-app") as client:
            client._get("player", {"wiki": "dota2"})

        request = respx.calls.last.request
        assert request.headers["User-Agent"] == f"my-app (via liquipydia/{__version__})"

    @respx.mock
    def test_authorization_header_present(self) -> None:
        """Verify Authorization header is set when API key is provided."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client(api_key="secret-key") as client:
            client._get("player", {"wiki": "dota2"})

        request = respx.calls.last.request
        assert request.headers["Authorization"] == "Apikey secret-key"

    @respx.mock
    def test_authorization_header_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify Authorization header is absent when no API key is provided."""
        monkeypatch.delenv("LIQUIPEDIA_API_KEY", raising=False)
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with LiquipediaClient("test-app", api_key=None) as client:
            client._get("player", {"wiki": "dota2"})

        request = respx.calls.last.request
        assert "Authorization" not in request.headers

    @respx.mock
    def test_accept_encoding_header(self) -> None:
        """Verify Accept-Encoding: gzip is set."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client._get("player", {"wiki": "dota2"})

        request = respx.calls.last.request
        assert "gzip" in request.headers["Accept-Encoding"]

    def test_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify API key falls back to LIQUIPEDIA_API_KEY env var."""
        monkeypatch.setenv("LIQUIPEDIA_API_KEY", "env-key")

        with LiquipediaClient("test-app") as client:
            auth = client._http.headers.get("Authorization")
            assert auth == "Apikey env-key"


# === Context Manager ===


class TestContextManager:
    """Tests for context manager protocol."""

    def test_enter_returns_self(self) -> None:
        """Verify __enter__ returns the client instance."""
        client = _make_client()
        assert client.__enter__() is client
        client.close()

    def test_exit_closes_client(self) -> None:
        """Verify __exit__ closes the HTTP session."""
        client = _make_client()

        with client:
            pass

        assert client._http.is_closed


# === Response Parsing ===


class TestParseResponse:
    """Tests for _parse_response behavior."""

    @respx.mock
    def test_successful_response(self) -> None:
        """Verify successful response returns result from API body."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": [{"name": "Miracle-"}]}))

        with _make_client() as client:
            response = client._get("player", {"wiki": "dota2"})

        assert response.result == [{"name": "Miracle-"}]

    @respx.mock
    def test_response_with_warnings(self) -> None:
        """Verify warnings from API body are forwarded."""
        respx.get(f"{BASE_URL}player").mock(
            return_value=httpx.Response(
                200,
                json={"result": [], "warning": ["deprecated field"]},
            )
        )

        with _make_client() as client:
            response = client._get("player", {"wiki": "dota2"})

        assert response.warnings == ["deprecated field"]

    @respx.mock
    def test_api_body_error(self) -> None:
        """Verify API body errors raise ApiError."""
        respx.get(f"{BASE_URL}player").mock(
            return_value=httpx.Response(200, json={"result": [], "error": ["unknown wiki"]})
        )

        with _make_client() as client, pytest.raises(ApiError, match="unknown wiki"):
            client._get("player", {"wiki": "badwiki"})


# === HTTP Error Handling ===


class TestHttpErrors:
    """Tests for HTTP status code error mapping."""

    @respx.mock
    def test_403_raises_auth_error(self) -> None:
        """Verify HTTP 403 raises AuthError."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(403))

        with _make_client() as client, pytest.raises(AuthError):
            client._get("player", {"wiki": "dota2"})

    @respx.mock
    def test_404_raises_not_found_error(self) -> None:
        """Verify HTTP 404 raises NotFoundError."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(404))

        with _make_client() as client, pytest.raises(NotFoundError):
            client._get("player", {"wiki": "dota2"})

    @respx.mock
    def test_500_raises_liquipedia_error(self) -> None:
        """Verify HTTP 500 raises LiquipediaError."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(500, text="Internal Server Error"))

        with _make_client() as client, pytest.raises(LiquipediaError, match="HTTP 500"):
            client._get("player", {"wiki": "dota2"})


# === Rate Limiting ===


class TestRateLimiting:
    """Tests for 429 retry behavior."""

    @respx.mock
    def test_429_retries_and_succeeds(self) -> None:
        """Verify client retries on 429 and succeeds when the next attempt works."""
        route = respx.get(f"{BASE_URL}player")
        route.side_effect = [
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"result": [{"id": 1}]}),
        ]

        with _make_client(max_retries=3, retry_backoff_factor=0.0) as client:
            response = client._get("player", {"wiki": "dota2"})

        assert response.result == [{"id": 1}]
        assert route.call_count == 2

    @respx.mock
    def test_429_exhausts_retries(self) -> None:
        """Verify RateLimitError is raised after max retries."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(429, headers={"Retry-After": "0"}))

        with _make_client(max_retries=2, retry_backoff_factor=0.0) as client, pytest.raises(RateLimitError):
            client._get("player", {"wiki": "dota2"})

    @respx.mock
    def test_429_uses_retry_after_header(self) -> None:
        """Verify RateLimitError carries the Retry-After value."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(429, headers={"Retry-After": "42"}))

        with _make_client(max_retries=0) as client, pytest.raises(RateLimitError) as exc_info:
            client._get("player", {"wiki": "dota2"})

        assert exc_info.value.retry_after == 42

    @respx.mock
    def test_429_non_numeric_retry_after(self) -> None:
        """Verify non-numeric Retry-After header falls back to computed backoff."""
        route = respx.get(f"{BASE_URL}player")
        route.side_effect = [
            httpx.Response(429, headers={"Retry-After": "not-a-number"}),
            httpx.Response(200, json={"result": [{"id": 1}]}),
        ]

        with _make_client(max_retries=3, retry_backoff_factor=0.0) as client:
            response = client._get("player", {"wiki": "dota2"})

        assert response.result == [{"id": 1}]


# === Pagination ===


class TestPagination:
    """Tests for the paginate method."""

    @respx.mock
    def test_paginate_single_page(self) -> None:
        """Verify pagination stops when a page returns fewer records than page_size."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": [{"id": 1}, {"id": 2}]}))

        with _make_client() as client:
            records = list(client.paginate("player", {"wiki": "dota2"}, page_size=10))

        assert records == [{"id": 1}, {"id": 2}]

    @respx.mock
    def test_paginate_multiple_pages(self) -> None:
        """Verify pagination fetches multiple pages."""
        route = respx.get(f"{BASE_URL}player")
        route.side_effect = [
            httpx.Response(200, json={"result": [{"id": 1}, {"id": 2}]}),
            httpx.Response(200, json={"result": [{"id": 3}]}),
        ]

        with _make_client() as client:
            records = list(client.paginate("player", {"wiki": "dota2"}, page_size=2))

        assert records == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert route.call_count == 2

    @respx.mock
    def test_paginate_max_results(self) -> None:
        """Verify pagination stops at max_results."""
        respx.get(f"{BASE_URL}player").mock(
            return_value=httpx.Response(200, json={"result": [{"id": i} for i in range(10)]})
        )

        with _make_client() as client:
            records = list(client.paginate("player", {"wiki": "dota2"}, page_size=10, max_results=3))

        assert len(records) == 3

    @respx.mock
    def test_paginate_does_not_mutate_params(self) -> None:
        """Verify pagination does not mutate the caller's params dict."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        params = {"wiki": "dota2"}

        with _make_client() as client:
            list(client.paginate("player", params, page_size=10))

        assert params == {"wiki": "dota2"}

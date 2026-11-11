"""Tests for the liquipydia core client."""

# Standard library
from contextlib import AbstractContextManager, nullcontext
import re

# Third-party
import httpx
import pytest
import respx

# Local
from _tests._helpers import BASE_URL, make_client
from liquipydia import (
    ApiError,
    AuthError,
    LiquipediaClient,
    LiquipediaError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    __version__,
)

# === Fixtures ===


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record the client's retry waits instead of sleeping."""
    recorded: list[float] = []
    monkeypatch.setattr("liquipydia._client.time.sleep", recorded.append)
    return recorded


# === Constructor & Headers ===


@respx.mock
@pytest.mark.parametrize(
    ("client_kwargs", "header", "pattern"),
    [
        pytest.param(
            {"app_name": "my-app"},
            "User-Agent",
            re.escape(f"my-app (via liquipydia/{__version__})"),
            id="user-agent",
        ),
        pytest.param({"api_key": "secret-key"}, "Authorization", "Apikey secret-key", id="authorization"),
        pytest.param({}, "Accept-Encoding", ".*gzip.*", id="accept-encoding-gzip"),
    ],
)
def test_request_header(client_kwargs: dict[str, object], header: str, pattern: str) -> None:
    """Verify the headers the client sends on every request."""
    respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

    with make_client(**client_kwargs) as client:
        client.get("player", {"wiki": "dota2"})

    assert re.fullmatch(pattern, respx.calls.last.request.headers[header])


def test_custom_transport_serves_requests() -> None:
    """Verify a transport passed to the constructor carries the client's requests."""
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """Record the requested path and answer with one record."""
        paths.append(request.url.path)
        return httpx.Response(200, json={"result": [{"id": 1}]})

    with make_client(transport=httpx.MockTransport(handler)) as client:
        assert client.get("player", {"wiki": "dota2"}).result == [{"id": 1}]

    assert paths == ["/api/v3/player"]


class TestConstructor:
    """Tests for LiquipediaClient API key resolution."""

    @respx.mock
    def test_authorization_header_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify Authorization header is absent when no API key is provided."""
        monkeypatch.delenv("LIQUIPEDIA_API_KEY", raising=False)
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with LiquipediaClient("test-app", api_key=None) as client:
            client.get("player", {"wiki": "dota2"})

        assert "Authorization" not in respx.calls.last.request.headers

    @staticmethod
    def test_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify API key falls back to LIQUIPEDIA_API_KEY env var."""
        monkeypatch.setenv("LIQUIPEDIA_API_KEY", "env-key")

        with LiquipediaClient("test-app") as client:
            auth = client._http.headers.get("Authorization")
            assert auth == "Apikey env-key"


# === Context Manager ===


class TestContextManager:
    """Tests for context manager protocol."""

    @staticmethod
    def test_enter_returns_self() -> None:
        """Verify __enter__ returns the client instance."""
        client = make_client()
        assert client.__enter__() is client
        client.close()

    @staticmethod
    def test_exit_closes_client() -> None:
        """Verify __exit__ closes the HTTP session."""
        client = make_client()

        with client:
            pass

        assert client._http.is_closed


# === Response Parsing ===


class TestParseResponse:
    """Tests for _parse_response on successful responses."""

    @respx.mock
    def test_successful_response(self) -> None:
        """Verify successful response returns result from API body."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": [{"name": "Miracle-"}]}))

        with make_client() as client:
            response = client.get("player", {"wiki": "dota2"})

        assert response.result == [{"name": "Miracle-"}]

    @respx.mock
    def test_response_with_warnings(self) -> None:
        """Verify warnings from API body are forwarded."""
        respx.get(f"{BASE_URL}player").mock(
            return_value=httpx.Response(200, json={"result": [], "warning": ["deprecated field"]})
        )

        with make_client() as client:
            response = client.get("player", {"wiki": "dota2"})

        assert response.warnings == ["deprecated field"]


# === Error Mapping ===


@respx.mock
@pytest.mark.parametrize(
    ("response", "error", "message"),
    [
        pytest.param(
            httpx.Response(200, json={"result": [], "error": ["unknown wiki"]}),
            ApiError,
            "unknown wiki",
            id="api-body-error",
        ),
        pytest.param(
            httpx.Response(200, content=b"not-json", headers={"content-type": "text/plain"}),
            LiquipediaError,
            "Failed to parse API response",
            id="malformed-json",
        ),
        pytest.param(
            httpx.Response(200, json=["unexpected", "list"]),
            LiquipediaError,
            "Unexpected API response format",
            id="non-dict-json",
        ),
        pytest.param(httpx.Response(403), AuthError, "Invalid or missing API key", id="http-403"),
        pytest.param(httpx.Response(404), NotFoundError, "Requested data does not exist", id="http-404"),
        pytest.param(httpx.Response(400, text="Bad Request"), LiquipediaError, "HTTP 400", id="http-400-lowest"),
        pytest.param(httpx.Response(500, text="Internal Server Error"), LiquipediaError, "HTTP 500", id="http-500"),
    ],
)
def test_error_mapping(response: httpx.Response, error: type[LiquipediaError], message: str) -> None:
    """Verify each failing response maps to its exception type and message."""
    respx.get(f"{BASE_URL}player").mock(return_value=response)

    with make_client() as client, pytest.raises(error, match=message):
        client.get("player", {"wiki": "dota2"})


# === Retries (HTTP 429 and timeouts) ===


def _rate_limited(retry_after: str | None = None) -> httpx.Response:
    """Build a 429 response, with a Retry-After header when given."""
    return httpx.Response(429, headers={"Retry-After": retry_after} if retry_after is not None else {})


def _ok() -> httpx.Response:
    """Build a successful response holding one record."""
    return httpx.Response(200, json={"result": [{"id": 1}]})


def _timeout() -> httpx.ReadTimeout:
    """Build the timeout raised when the server does not answer in time."""
    return httpx.ReadTimeout("The read operation timed out")


def _expected_outcome(last: httpx.Response | Exception) -> AbstractContextManager[object]:
    """Return what the final attempt should lead to: a retry-exhausted error, or a successful call."""
    if isinstance(last, httpx.TimeoutException):
        return pytest.raises(NetworkError, match="timed out")
    if isinstance(last, httpx.Response) and last.status_code == 429:
        return pytest.raises(RateLimitError)
    return nullcontext()


@respx.mock
@pytest.mark.parametrize(
    ("responses", "max_retries", "backoff_factor", "expected_sleeps"),
    [
        # --- HTTP 429 ---
        pytest.param([_rate_limited("0"), _ok()], 3, 0.0, [0.0], id="429-succeeds-after-retry"),
        pytest.param([_rate_limited("0") for _ in range(3)], 2, 0.0, [0.0, 0.0], id="429-exhausts-retries"),
        pytest.param([_rate_limited("not-a-number"), _ok()], 3, 0.0, [0.0], id="429-non-numeric-retry-after"),
        pytest.param([_rate_limited() for _ in range(4)], 3, 1.0, [1.0, 2.0, 4.0], id="429-backoff-doubles"),
        pytest.param([_rate_limited("5"), _ok()], 1, 1.0, [5], id="429-retry-after-wins-over-backoff"),
        # --- Timeouts ---
        pytest.param([_timeout(), _ok()], 3, 1.0, [1.0], id="timeout-succeeds-after-retry"),
        pytest.param([_timeout() for _ in range(3)], 2, 1.0, [1.0, 2.0], id="timeout-exhausts-retries"),
        pytest.param([_timeout()], 0, 1.0, [], id="timeout-no-retries"),
        # --- Mixed: both share one retry budget ---
        pytest.param([_timeout(), _rate_limited("0"), _ok()], 2, 1.0, [1.0, 2.0], id="timeout-then-429-then-ok"),
        pytest.param([_rate_limited("0"), _timeout()], 1, 1.0, [1.0], id="429-then-timeout-exhausts"),
    ],
)
def test_retries(
    sleeps: list[float],
    responses: list[httpx.Response | Exception],
    max_retries: int,
    backoff_factor: float,
    expected_sleeps: list[float],
) -> None:
    """Verify the retry loop: one request per attempt, the waits between them, and the final outcome.

    A last 429 means RateLimitError and a last timeout means NetworkError (retries exhausted); anything else succeeds.
    """
    route = respx.get(f"{BASE_URL}player")
    route.side_effect = responses

    with (
        _expected_outcome(responses[-1]),
        make_client(max_retries=max_retries, retry_backoff_factor=backoff_factor) as client,
    ):
        assert client.get("player", {"wiki": "dota2"}).result == [{"id": 1}]

    assert sleeps == expected_sleeps
    assert route.call_count == len(responses)


@respx.mock
@pytest.mark.parametrize(
    "error",
    [
        pytest.param(httpx.ConnectError("Connection refused"), id="connect-error"),
        pytest.param(httpx.RemoteProtocolError("Server disconnected without sending a response"), id="protocol-error"),
        pytest.param(httpx.TooManyRedirects("Exceeded maximum allowed redirects"), id="too-many-redirects"),
    ],
)
def test_network_error_not_retried(sleeps: list[float], error: httpx.RequestError) -> None:
    """Verify non-timeout request failures raise NetworkError at once, chained to the original httpx error."""
    route = respx.get(f"{BASE_URL}player")
    route.side_effect = error

    with make_client(max_retries=3) as client, pytest.raises(NetworkError, match="Request failed") as exc_info:
        client.get("player", {"wiki": "dota2"})

    assert exc_info.value.__cause__ is error
    assert isinstance(exc_info.value, LiquipediaError)
    assert route.call_count == 1
    assert sleeps == []


@respx.mock
def test_timeout_error_message_and_cause(sleeps: list[float]) -> None:
    """Verify an exhausted timeout reports the number of attempts and keeps the original httpx exception as cause."""
    error = _timeout()
    respx.get(f"{BASE_URL}player").side_effect = error

    with make_client(max_retries=1, retry_backoff_factor=0.0) as client, pytest.raises(NetworkError) as exc_info:
        client.get("player", {"wiki": "dota2"})

    assert exc_info.value.message.startswith("Request timed out after 2 attempt(s): ")
    assert exc_info.value.__cause__ is error
    assert sleeps == [0.0]


@respx.mock
def test_429_error_carries_retry_after() -> None:
    """Verify RateLimitError carries the Retry-After value."""
    respx.get(f"{BASE_URL}player").mock(return_value=_rate_limited("42"))

    with make_client(max_retries=0) as client, pytest.raises(RateLimitError) as exc_info:
        client.get("player", {"wiki": "dota2"})

    assert exc_info.value.retry_after == 42


# === Pagination ===


class TestPagination:
    """Tests for the paginate method."""

    @respx.mock
    def test_paginate_single_page(self) -> None:
        """Verify pagination stops when a page returns fewer records than page_size."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": [{"id": 1}, {"id": 2}]}))

        with make_client() as client:
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

        with make_client() as client:
            records = list(client.paginate("player", {"wiki": "dota2"}, page_size=2))

        assert records == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert route.call_count == 2
        offsets = [route.calls[i].request.url.params["offset"] for i in range(2)]
        assert offsets == ["0", "2"]

    @respx.mock
    def test_paginate_page_size_one(self) -> None:
        """Verify page_size=1 (the smallest valid size) is accepted."""
        route = respx.get(f"{BASE_URL}player")
        route.side_effect = [
            httpx.Response(200, json={"result": [{"id": 1}]}),
            httpx.Response(200, json={"result": []}),
        ]

        with make_client() as client:
            records = list(client.paginate("player", {"wiki": "dota2"}, page_size=1))

        assert records == [{"id": 1}]
        assert route.call_count == 2

    @respx.mock
    def test_paginate_max_results(self) -> None:
        """Verify pagination stops at max_results."""
        respx.get(f"{BASE_URL}player").mock(
            return_value=httpx.Response(200, json={"result": [{"id": i} for i in range(10)]})
        )

        with make_client() as client:
            records = list(client.paginate("player", {"wiki": "dota2"}, page_size=10, max_results=3))

        assert len(records) == 3

    @respx.mock
    def test_paginate_does_not_mutate_params(self) -> None:
        """Verify pagination does not mutate the caller's params dict."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        params = {"wiki": "dota2"}

        with make_client() as client:
            list(client.paginate("player", params, page_size=10))

        assert params == {"wiki": "dota2"}

    @staticmethod
    def test_paginate_invalid_page_size() -> None:
        """Verify paginate() raises ValueError when page_size < 1."""
        with make_client() as client, pytest.raises(ValueError, match="page_size must be >= 1"):
            list(client.paginate("player", {"wiki": "dota2"}, page_size=0))

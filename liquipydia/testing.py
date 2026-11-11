"""Test helpers: an in-memory LPDB serving canned records to a real ``LiquipediaClient``.

Code that uses liquipydia can be tested without network access or an API key::

    from liquipydia.testing import FakeLpdb

    fake = FakeLpdb({"match": [{"match2id": "m1", "wiki": "rocketleague"}]})
    with fake.client() as client:
        records = list(client.matches.paginate("rocketleague"))
    assert fake.requests[0].endpoint == "match"

The client is a genuine ``LiquipediaClient``: only its network layer is replaced, so keyword filters, ``query``
validation, pagination, retries and error mapping behave exactly as in production.
"""

# Standard library
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

# Third-party
import httpx2

# Local
from liquipydia._client import LiquipediaClient

__all__ = ["FakeLpdb", "RecordedRequest"]

# === Constants ===

_API_PREFIX = "/api/v3/"

# Every endpoint the client can call: the 14 standard resources, plus the two team template endpoints (kept in sync
# with the resource classes by a unit test).
_ENDPOINTS: frozenset[str] = frozenset(
    {
        "broadcasters",
        "company",
        "datapoint",
        "externalmedialink",
        "match",
        "placement",
        "player",
        "series",
        "squadplayer",
        "standingsentry",
        "standingstable",
        "team",
        "teamtemplate",
        "teamtemplatelist",
        "tournament",
        "transfer",
    }
)


# === Records ===


@dataclass(frozen=True)
class RecordedRequest:
    """One request received by a :class:`FakeLpdb`.

    Attributes:
        endpoint: The LPDB endpoint called (e.g. ``"match"``).
        params: The query parameters sent, as strings (e.g. ``{"wiki": "dota2", "limit": "50", ...}``).
    """

    endpoint: str
    params: dict[str, str]


@dataclass
class _Failure:
    """A failure an endpoint answers with: an HTTP ``status``, or a timeout when ``None``.

    It applies to the next ``remaining`` requests, or to every request when ``remaining`` is ``None``.
    """

    status: int | None
    remaining: int | None


# === Fake LPDB ===


class FakeLpdb:
    """An in-memory LPDB serving canned records to real ``LiquipediaClient`` instances.

    Records are keyed by LPDB endpoint name (``"match"``, ``"player"``, ``"teamtemplate"``...). Each request returns the
    endpoint's records, sliced by ``offset`` / ``limit`` so pagination works, and reduced to the fields named in
    ``query`` when given. ``conditions`` and keyword filters are **not** evaluated: every record of the endpoint is
    returned, and :attr:`requests` shows what was asked. ``query`` functions (``sum::prizemoney``) are not computed
    either; such items are left out of the returned records.

    Args:
        records: Initial records per endpoint name.

    Raises:
        ValueError: If an endpoint name is unknown.
    """

    def __init__(self, records: Mapping[str, Iterable[dict[str, Any]]] | None = None) -> None:
        """Create the fake, optionally with initial records per endpoint name."""
        self._records: dict[str, list[dict[str, Any]]] = {}
        self._failures: dict[str, _Failure] = {}
        self._requests: list[RecordedRequest] = []
        for endpoint, endpoint_records in (records or {}).items():
            self.add(endpoint, *endpoint_records)

    # --- Setup ---

    def add(self, endpoint: str, *records: dict[str, Any]) -> None:
        """Add records served by an endpoint, after any it already serves.

        Args:
            endpoint: LPDB endpoint name (e.g. ``"match"``).
            *records: Records as returned by the API (plain dicts).

        Raises:
            ValueError: If the endpoint name is unknown.
        """
        self._records.setdefault(_check_endpoint(endpoint), []).extend(records)

    def fail(
        self, endpoint: str, *, status: int | None = None, timeout: bool = False, times: int | None = None
    ) -> None:
        """Make an endpoint fail, with an HTTP status or a timeout.

        The client then raises what it raises against the real API: ``RateLimitError`` for ``429`` (after its
        retries), ``AuthError`` for ``403``, ``NotFoundError`` for ``404``, ``LiquipediaError`` for other statuses, and
        ``NetworkError`` for a timeout (after its retries).

        Args:
            endpoint: LPDB endpoint name.
            status: HTTP status code to answer with (``>= 400``).
            timeout: Make requests time out instead.
            times: Fail only the next ``times`` requests, then serve records again; ``None`` fails every request.

        Raises:
            ValueError: If the endpoint is unknown, or not exactly one of ``status`` / ``timeout`` is given.
        """
        if (status is None) == (not timeout):
            raise ValueError("Pass exactly one of status=... or timeout=True")
        if status is not None and status < 400:
            raise ValueError(f"status must be an HTTP error code (>= 400), got {status}")
        self._failures[_check_endpoint(endpoint)] = _Failure(status, times)

    def client(
        self, app_name: str = "liquipydia-fake", *, max_retries: int = 3, retry_backoff_factor: float = 0.0
    ) -> LiquipediaClient:
        """Create a real ``LiquipediaClient`` whose requests are served by this fake (no network, no API key).

        Args:
            app_name: Application name used in the User-Agent header.
            max_retries: Retries on simulated HTTP 429 responses and timeouts, as for a real client.
            retry_backoff_factor: Backoff base between those retries; ``0.0`` by default so tests do not wait.

        Returns:
            The client; use it as a context manager.
        """
        return LiquipediaClient(
            app_name,
            api_key="fake-api-key",
            max_retries=max_retries,
            retry_backoff_factor=retry_backoff_factor,
            transport=httpx2.MockTransport(self._handle),
        )

    # --- Inspection ---

    @property
    def requests(self) -> list[RecordedRequest]:
        """Every request received so far, in order (a copy)."""
        return list(self._requests)

    # --- Serving ---

    def _take_failure(self, endpoint: str) -> _Failure | None:
        """Return the failure to answer this request with, if any, counting it against its ``remaining`` budget."""
        failure = self._failures.get(endpoint)
        if failure is not None and failure.remaining is not None:
            failure.remaining -= 1
            if failure.remaining == 0:
                del self._failures[endpoint]
        return failure

    def _handle(self, request: httpx2.Request) -> httpx2.Response:
        """Answer one request from the client: a simulated failure, or the endpoint's records."""
        endpoint = request.url.path.removeprefix(_API_PREFIX)
        params: dict[str, str] = dict(request.url.params.items())
        self._requests.append(RecordedRequest(endpoint, params))

        failure = self._take_failure(endpoint)
        if failure is not None:
            if failure.status is None:
                raise httpx2.ReadTimeout("Simulated timeout (FakeLpdb)", request=request)
            return httpx2.Response(failure.status, json={"error": [f"Simulated HTTP {failure.status}"]})

        records = self._records.get(endpoint, [])
        if "limit" in params:  # standard endpoints always send limit and offset; team template ones neither
            start = int(params.get("offset", "0"))
            end = start + int(params["limit"])
            records = records[start:end]
        query = params.get("query")
        if query:
            records = [_project(record, query) for record in records]
        return httpx2.Response(200, json={"result": records})


# === Helpers ===


def _check_endpoint(endpoint: str) -> str:
    """Return ``endpoint`` if the client can call it.

    Raises:
        ValueError: If it is not one of the endpoints the client can call.
    """
    if endpoint not in _ENDPOINTS:
        raise ValueError(f"Unknown LPDB endpoint {endpoint!r}. Valid endpoints: {sorted(_ENDPOINTS)}")
    return endpoint


def _project(record: dict[str, Any], query: str) -> dict[str, Any]:
    """Reduce a record to the plain fields named in ``query`` (case-insensitive), plus ``wiki`` as LPDB adds it."""
    wanted = {item.strip().lower() for item in query.split(",") if "::" not in item} | {"wiki"}
    return {key: value for key, value in record.items() if key.lower() in wanted}

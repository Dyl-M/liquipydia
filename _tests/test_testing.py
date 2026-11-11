"""Tests for liquipydia.testing (the in-memory FakeLpdb)."""

# Standard library
from collections.abc import Callable
from typing import Any

# Third-party
import pytest

# Local
from liquipydia import (
    AuthError,
    LiquipediaClient,
    LiquipediaError,
    Match,
    NetworkError,
    NotFoundError,
    RateLimitError,
)
from liquipydia.testing import FakeLpdb, RecordedRequest

MATCHES = [{"match2id": f"m{i}", "wiki": "rocketleague", "winner": "1", "bestof": 5} for i in range(5)]


# === Serving records ===


def test_client_is_real_and_needs_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify fake.client() is a genuine LiquipediaClient that ignores LIQUIPEDIA_API_KEY."""
    monkeypatch.setenv("LIQUIPEDIA_API_KEY", "real-key-must-not-be-used")

    with FakeLpdb().client() as client:
        assert isinstance(client, LiquipediaClient)
        assert client._http.headers["Authorization"] == "Apikey fake-api-key"


def test_list_serves_records_and_logs_request() -> None:
    """Verify list() returns the endpoint's records, which parse into models, and the request is recorded."""
    fake = FakeLpdb({"match": MATCHES})

    with fake.client() as client:
        response = client.matches.list("rocketleague", winner="1", limit=2)

    assert [Match.model_validate(record).match2id for record in response.result] == ["m0", "m1"]
    assert fake.requests == [
        RecordedRequest("match", {"wiki": "rocketleague", "conditions": "[[winner::1]]", "limit": "2", "offset": "0"})
    ]


def test_paginate_walks_pages() -> None:
    """Verify paginate() fetches every page through limit/offset slicing."""
    fake = FakeLpdb({"match": MATCHES})

    with fake.client() as client:
        records = list(client.matches.paginate("rocketleague", page_size=2))

    assert [record["match2id"] for record in records] == ["m0", "m1", "m2", "m3", "m4"]
    assert [request.params["offset"] for request in fake.requests] == ["0", "2", "4"]


def test_raw_get_with_limit_only_starts_at_first_record() -> None:
    """Verify a direct client.get() sending a limit without an offset is served from the first record."""
    fake = FakeLpdb({"match": MATCHES})

    with fake.client() as client:
        response = client.get("match", {"wiki": "rocketleague", "limit": 2})

    assert response.result == MATCHES[:2]


def test_add_appends_and_unknown_endpoint_is_empty() -> None:
    """Verify add() appends after existing records, and an endpoint without records answers an empty page."""
    fake = FakeLpdb({"player": [{"pagename": "A"}]})
    fake.add("player", {"pagename": "B"}, {"pagename": "C"})

    with fake.client() as client:
        assert [r["pagename"] for r in client.players.list("dota2").result] == ["A", "B", "C"]
        assert client.teams.list("dota2").result == []


def test_query_projects_plain_fields() -> None:
    """Verify query keeps the named fields (case-insensitive) plus wiki, and leaves out function items."""
    fake = FakeLpdb({"placement": [{"pagename": "P", "prizemoney": 100, "tournament": "T", "wiki": "dota2"}]})

    with fake.client() as client:
        response = client.placements.list("dota2", query="PrizeMoney, sum::prizemoney")

    assert response.result == [{"prizemoney": 100, "wiki": "dota2"}]


def test_team_template_endpoints_not_sliced() -> None:
    """Verify the team template endpoints (which send no limit) return every record."""
    templates = [{"template": f"t{i}"} for i in range(3)]
    fake = FakeLpdb({"teamtemplate": templates[:1], "teamtemplatelist": templates})

    with fake.client() as client:
        assert client.team_templates.get("dota2", "t0").result == templates[:1]
        assert client.team_template_list.list("dota2").result == templates


def test_client_side_validation_still_applies() -> None:
    """Verify the real client validation runs: an invalid query raises before reaching the fake."""
    fake = FakeLpdb({"match": MATCHES})

    with fake.client() as client, pytest.raises(ValueError, match="Unknown query field"):
        client.matches.list("rocketleague", query="notafield")

    assert fake.requests == []


# === Simulated failures ===


@pytest.mark.parametrize(
    ("failure", "error", "expected_requests"),
    [
        pytest.param({"status": 403}, AuthError, 1, id="403-auth"),
        pytest.param({"status": 404}, NotFoundError, 1, id="404-not-found"),
        pytest.param({"status": 500}, LiquipediaError, 1, id="500-generic"),
        pytest.param({"status": 429}, RateLimitError, 3, id="429-after-retries"),
        pytest.param({"timeout": True}, NetworkError, 3, id="timeout-after-retries"),
    ],
)
def test_fail_raises_real_errors(failure: dict[str, Any], error: type[Exception], expected_requests: int) -> None:
    """Verify a failing endpoint makes the real client raise its usual error, retries included."""
    fake = FakeLpdb({"match": MATCHES})
    fake.fail("match", **failure)

    with fake.client(max_retries=2) as client, pytest.raises(error):
        client.matches.list("rocketleague")

    assert len(fake.requests) == expected_requests


def test_fail_times_then_recovers() -> None:
    """Verify fail(times=N) fails N requests then serves records, so the client's retries succeed."""
    fake = FakeLpdb({"match": MATCHES})
    fake.fail("match", status=429, times=2)

    with fake.client(max_retries=3) as client:
        response = client.matches.list("rocketleague", limit=1)

    assert response.result == MATCHES[:1]
    assert len(fake.requests) == 3


def test_fail_only_affects_its_endpoint() -> None:
    """Verify a failure set on one endpoint leaves the others serving records."""
    fake = FakeLpdb({"match": MATCHES, "player": [{"pagename": "A"}]})
    fake.fail("match", status=404)

    with fake.client() as client:
        assert client.players.list("dota2").result == [{"pagename": "A"}]


# === Argument checks ===


@pytest.mark.parametrize(
    ("action", "message"),
    [
        pytest.param(lambda fake: fake.add("matches", {}), "Unknown LPDB endpoint 'matches'", id="add-unknown"),
        pytest.param(lambda fake: FakeLpdb({"nope": []}), "Unknown LPDB endpoint 'nope'", id="init-unknown"),
        pytest.param(lambda fake: fake.fail("nope", status=500), "Unknown LPDB endpoint", id="fail-unknown"),
        pytest.param(lambda fake: fake.fail("match"), "exactly one of", id="fail-neither"),
        pytest.param(lambda fake: fake.fail("match", status=500, timeout=True), "exactly one of", id="fail-both"),
        pytest.param(lambda fake: fake.fail("match", status=399), r"HTTP error code \(>= 400\)", id="fail-not-error"),
    ],
)
def test_rejects_invalid_arguments(action: Callable[[FakeLpdb], object], message: str) -> None:
    """Verify unknown endpoint names and inconsistent fail() arguments raise ValueError."""
    with pytest.raises(ValueError, match=message):
        action(FakeLpdb())


def test_fail_accepts_lowest_error_status() -> None:
    """Verify 400 is accepted as a failure status."""
    fake = FakeLpdb()
    fake.fail("match", status=400)

    with fake.client() as client, pytest.raises(LiquipediaError, match="HTTP 400"):
        client.matches.list("rocketleague")


def test_requests_returns_a_copy() -> None:
    """Verify mutating the returned request list does not alter the fake's log."""
    fake = FakeLpdb()
    with fake.client() as client:
        client.players.list("dota2")

    fake.requests.clear()
    assert len(fake.requests) == 1

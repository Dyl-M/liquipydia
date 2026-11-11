"""Tests for the liquipydia resource layer."""

# Standard library
from collections.abc import Callable
import datetime as dt
from typing import Any

# Third-party
import httpx
import pytest
import respx

# Local
from _tests._helpers import BASE_URL, get_query_params, make_client
from liquipydia import (
    ApiResponse,
    BroadcastersResource,
    CompaniesResource,
    DatapointsResource,
    ExternalMediaLinksResource,
    LiquipediaClient,
    MatchResource,
    PlacementsResource,
    PlayersResource,
    Resource,
    SeriesResource,
    SquadPlayersResource,
    StandingsEntriesResource,
    StandingsTablesResource,
    TeamsResource,
    TeamTemplateListResource,
    TeamTemplateResource,
    TournamentsResource,
    TransfersResource,
)
from liquipydia._resources import _is_date_type

ResourceCall = Callable[[LiquipediaClient], object]

# === Sent Parameters ===

# (endpoint, call, expected params): a None value means the param must be absent from the request.
SENT_PARAMS_CASES = [
    # --- Base Resource ---
    pytest.param(
        "player",
        lambda client: client.players.list("dota2"),
        {
            "wiki": "dota2",
            "limit": "50",
            "offset": "0",
            "conditions": None,
            "query": None,
            "order": None,
            "groupby": None,
        },
        id="list-defaults",
    ),
    pytest.param(
        "player",
        lambda client: client.players.list("dota2", conditions="[[name::Miracle-]]"),
        {"conditions": "[[name::Miracle-]]"},
        id="list-conditions",
    ),
    pytest.param(
        "player",
        lambda client: client.players.list(
            "dota2",
            conditions="[[name::Miracle-]]",
            query="name,id",
            limit=10,
            offset=5,
            order="name ASC",
            groupby="nationality",
        ),
        {
            "conditions": "[[name::Miracle-]]",
            "query": "name,id",
            "limit": "10",
            "offset": "5",
            "order": "name ASC",
            "groupby": "nationality",
        },
        id="list-all-params",
    ),
    pytest.param(
        "player",
        lambda client: list(client.players.paginate("dota2")),
        {"conditions": None, "order": None, "rawstreams": None, "streamurls": None},
        id="paginate-defaults",
    ),
    # --- Keyword Filters ---
    pytest.param(
        "player",
        lambda client: client.players.list("rocketleague", name="Zen"),
        {"conditions": "[[name::Zen]]"},
        id="filter-single",
    ),
    pytest.param(
        "player",
        lambda client: client.players.list("rocketleague", name="Zen", nationality="fr"),
        {"conditions": "[[name::Zen]] AND [[nationality::fr]]"},
        id="filter-multiple",
    ),
    pytest.param(
        "player",
        lambda client: client.players.list("rocketleague", conditions="[[team::Vitality]]", name="Zen"),
        {"conditions": "[[team::Vitality]] AND [[name::Zen]]"},
        id="filter-with-conditions",
    ),
    pytest.param(
        "placement",
        lambda client: client.placements.list("dota2", prizemoney=">10000"),
        {"conditions": "[[prizemoney::>10000]]"},
        id="filter-operator",
    ),
    pytest.param(
        "player",
        lambda client: list(client.players.paginate("rocketleague", name="Zen")),
        {"conditions": "[[name::Zen]]"},
        id="filter-paginate",
    ),
    pytest.param(
        "match",
        lambda client: client.matches.list("rocketleague", rawstreams=True, winner="1"),
        {"conditions": "[[winner::1]]", "rawstreams": "true"},
        id="filter-with-streams",
    ),
    # --- Match Resource ---
    pytest.param(
        "match",
        lambda client: client.matches.list("dota2", rawstreams=True),
        {"rawstreams": "true"},
        id="match-rawstreams",
    ),
    pytest.param(
        "match",
        lambda client: client.matches.list("dota2", streamurls=True),
        {"streamurls": "true"},
        id="match-streamurls",
    ),
    pytest.param(
        "match",
        lambda client: client.matches.list("dota2"),
        {"rawstreams": None, "streamurls": None},
        id="match-defaults-exclude-streams",
    ),
    pytest.param(
        "match",
        lambda client: list(client.matches.paginate("dota2", rawstreams=True, streamurls=True)),
        {"rawstreams": "true", "streamurls": "true"},
        id="match-paginate-streams",
    ),
    # --- Team Template Resources ---
    pytest.param(
        "teamtemplate",
        lambda client: client.team_templates.get("dota2", "teamliquid"),
        {"wiki": "dota2", "template": "teamliquid", "date": None},
        id="teamtemplate-defaults",
    ),
    pytest.param(
        "teamtemplate",
        lambda client: client.team_templates.get("dota2", "teamliquid", date="2009-06-05"),
        {"date": "2009-06-05"},
        id="teamtemplate-date",
    ),
    pytest.param(
        "teamtemplatelist",
        lambda client: client.team_template_list.list("dota2"),
        {"wiki": "dota2", "pagination": None},
        id="teamtemplatelist-defaults",
    ),
    pytest.param(
        "teamtemplatelist",
        lambda client: client.team_template_list.list("dota2", pagination=2),
        {"pagination": "2"},
        id="teamtemplatelist-pagination",
    ),
    # --- Query validation: accepted items, string sent unchanged ---
    pytest.param(
        "player",
        lambda client: client.players.list("dota2", query="pagename, name"),
        {"query": "pagename, name"},
        id="query-spaces-sent-unchanged",
    ),
    pytest.param(
        "placement",
        lambda client: client.placements.list("dota2", query="tournament,sum::prizemoney"),
        {"query": "tournament,sum::prizemoney"},
        id="query-function",
    ),
    pytest.param(
        "placement",
        lambda client: client.placements.list("dota2", query="SUM::prizemoney"),
        {"query": "SUM::prizemoney"},
        id="query-function-uppercase",
    ),
    pytest.param(
        "player",
        lambda client: list(client.players.paginate("dota2", query="pagename,month::birthdate")),
        {"query": "pagename,month::birthdate"},
        id="query-paginate",
    ),
    pytest.param(
        "placement",
        lambda client: client.placements.list("dota2", query="PrizeMoney"),
        {"query": "PrizeMoney"},
        id="query-field-mixed-case",
    ),
    pytest.param(
        "match",
        lambda client: client.matches.list("dota2", query="year::date"),
        {"query": "year::date"},
        id="query-date-function-on-datetime",
    ),
    pytest.param(
        "player",
        lambda client: client.players.list("dota2", query=""),
        {"query": None},
        id="query-empty-not-checked",
    ),
]


@respx.mock
@pytest.mark.parametrize(("endpoint", "call", "expected"), SENT_PARAMS_CASES)
def test_sent_params(endpoint: str, call: ResourceCall, expected: dict[str, str | None]) -> None:
    """Verify each call hits its endpoint and sends the expected query params (None = absent)."""
    route = respx.get(f"{BASE_URL}{endpoint}").mock(return_value=httpx.Response(200, json={"result": []}))

    with make_client() as client:
        call(client)

    assert route.called
    params = get_query_params(respx.calls.last.request)
    assert {key: params.get(key) for key in expected} == expected


# === Client-Side Validation (filter keys and query items) ===


@respx.mock
@pytest.mark.parametrize(
    ("call", "message"),
    [
        # --- Filter keys ---
        pytest.param(
            lambda client: client.players.list("rocketleague", **{"bad key!": "value"}),
            "Invalid filter key",
            id="filter-invalid-key",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", fakefield="value"),
            "Unknown filter key 'fakefield'",
            id="filter-unknown-key",
        ),
        pytest.param(
            lambda client: list(client.players.paginate("rocketleague", fakefield="value")),
            "Unknown filter key 'fakefield'",
            id="filter-paginate-unknown-key",
        ),
        # --- Query items ---
        pytest.param(
            lambda client: client.players.list("rocketleague", query="pagename,notafield"),
            "Unknown query field 'notafield' for this resource",
            id="query-unknown-field",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="sum::notafield"),
            "Unknown query field 'notafield'",
            id="query-function-unknown-field",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="summ::earnings"),
            "Unknown query function 'summ' in 'summ::earnings'",
            id="query-unknown-function",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="::earnings"),
            "Unknown query function ''",
            id="query-empty-function",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="pagename,,name"),
            "Empty field in query",
            id="query-empty-item",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="pagename, "),
            "Empty field in query",
            id="query-trailing-separator",
        ),
        pytest.param(
            lambda client: list(client.players.paginate("rocketleague", query="notafield")),
            "Unknown query field 'notafield'",
            id="query-paginate-unknown-field",
        ),
        pytest.param(
            lambda client: client.placements.list("rocketleague", query="birthdate"),
            "Unknown query field 'birthdate'",
            id="query-field-of-another-resource",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="year::earnings"),
            "Date function 'year' in 'year::earnings' needs a date field",
            id="query-date-function-on-number",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="sum :: earnings"),
            "Unknown query function 'sum '",
            id="query-spaces-around-separator",
        ),
        pytest.param(
            lambda client: client.players.list("rocketleague", query="sum::sum::earnings"),
            "Unknown query function 'sum::sum'",
            id="query-multiple-separators",
        ),
    ],
)
def test_rejects_invalid_input(call: ResourceCall, message: str) -> None:
    """Verify invalid filter keys and query items raise ValueError before any request is sent."""
    route = respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

    with make_client() as client, pytest.raises(ValueError, match=message):
        call(client)

    assert not route.called


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        pytest.param(dt.date, True, id="date"),
        pytest.param(dt.datetime, True, id="datetime"),
        pytest.param(dt.date | None, True, id="optional-date"),
        pytest.param(dt.datetime | None, True, id="optional-datetime"),
        pytest.param(int | None, False, id="optional-int"),
        pytest.param(str, False, id="str"),
        pytest.param(dict[str, Any] | None, False, id="optional-generic"),
    ],
)
def test_is_date_type(annotation: object, expected: bool) -> None:
    """Verify which model field annotations count as dates for the query date functions."""
    assert _is_date_type(annotation) is expected


# === Responses ===


class TestResourceResponses:
    """Tests for what the base Resource methods return."""

    @respx.mock
    def test_list_returns_api_response(self) -> None:
        """Verify list() returns an ApiResponse instance."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": [{"name": "Miracle-"}]}))

        with make_client() as client:
            response = client.players.list("dota2")

        assert isinstance(response, ApiResponse)
        assert response.result == [{"name": "Miracle-"}]

    @respx.mock
    def test_paginate_yields_records(self) -> None:
        """Verify paginate() yields individual records."""
        route = respx.get(f"{BASE_URL}player")
        route.side_effect = [
            httpx.Response(200, json={"result": [{"id": 1}, {"id": 2}]}),
            httpx.Response(200, json={"result": [{"id": 3}]}),
        ]

        with make_client() as client:
            records = list(client.players.paginate("dota2", page_size=2))

        assert records == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert route.call_count == 2


# === Client Resource Attributes ===


@pytest.mark.parametrize(
    ("attribute", "resource_cls"),
    [
        ("broadcasters", BroadcastersResource),
        ("companies", CompaniesResource),
        ("datapoints", DatapointsResource),
        ("external_media_links", ExternalMediaLinksResource),
        ("matches", MatchResource),
        ("placements", PlacementsResource),
        ("players", PlayersResource),
        ("series", SeriesResource),
        ("squad_players", SquadPlayersResource),
        ("standings_entries", StandingsEntriesResource),
        ("standings_tables", StandingsTablesResource),
        ("teams", TeamsResource),
        ("tournaments", TournamentsResource),
        ("transfers", TransfersResource),
        ("team_templates", TeamTemplateResource),
        ("team_template_list", TeamTemplateListResource),
    ],
)
def test_resource_attached(attribute: str, resource_cls: type) -> None:
    """Verify each of the 16 resource attributes exists with the correct type."""
    with make_client() as client:
        assert isinstance(getattr(client, attribute), resource_cls)


@pytest.mark.parametrize(
    ("attribute", "endpoint"),
    [
        ("players", "player"),
        ("teams", "team"),
        ("broadcasters", "broadcasters"),
        ("matches", "match"),
        ("external_media_links", "externalmedialink"),
    ],
)
def test_resource_endpoint(attribute: str, endpoint: str) -> None:
    """Verify standard resources inherit from Resource and point to the correct endpoint string."""
    with make_client() as client:
        resource = getattr(client, attribute)
        assert isinstance(resource, Resource)
        assert resource._endpoint == endpoint

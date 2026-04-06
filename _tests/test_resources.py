"""Tests for the liquipydia resource layer."""

# Standard library
from urllib.parse import parse_qs

# Third-party
import httpx
import respx

# Local
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

BASE_URL = "https://api.liquipedia.net/api/v3/"


# === Helpers ===


def _make_client(**kwargs: object) -> LiquipediaClient:
    """Create a client with defaults suitable for testing."""
    defaults: dict[str, object] = {"app_name": "test-app", "api_key": "test-key", "timeout": 5.0}
    defaults.update(kwargs)
    return LiquipediaClient(**defaults)  # type: ignore[arg-type]


def _get_query_params(request: httpx.Request) -> dict[str, str]:
    """Extract query parameters from a request as a flat dict."""
    parsed = parse_qs(str(request.url.params))
    return {k: v[0] for k, v in parsed.items()}


# === Base Resource ===


class TestResource:
    """Tests for the base Resource class using the players' endpoint."""

    @respx.mock
    def test_list_sends_correct_endpoint(self) -> None:
        """Verify list() sends a GET to the correct endpoint URL."""
        route = respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("dota2")

        assert route.called

    @respx.mock
    def test_list_passes_wiki_param(self) -> None:
        """Verify wiki parameter is included in the request."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("dota2")

        params = _get_query_params(respx.calls.last.request)
        assert params["wiki"] == "dota2"

    @respx.mock
    def test_list_passes_conditions(self) -> None:
        """Verify conditions parameter is forwarded."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("dota2", conditions="[[name::Miracle-]]")

        params = _get_query_params(respx.calls.last.request)
        assert params["conditions"] == "[[name::Miracle-]]"

    @respx.mock
    def test_list_excludes_none_params(self) -> None:
        """Verify None-valued optional parameters are excluded from the request."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("dota2")

        params = _get_query_params(respx.calls.last.request)
        assert "conditions" not in params
        assert "query" not in params
        assert "order" not in params
        assert "groupby" not in params

    @respx.mock
    def test_list_default_limit(self) -> None:
        """Verify default limit is 50."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("dota2")

        params = _get_query_params(respx.calls.last.request)
        assert params["limit"] == "50"

    @respx.mock
    def test_list_returns_api_response(self) -> None:
        """Verify list() returns an ApiResponse instance."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": [{"name": "Miracle-"}]}))

        with _make_client() as client:
            response = client.players.list("dota2")

        assert isinstance(response, ApiResponse)
        assert response.result == [{"name": "Miracle-"}]

    @respx.mock
    def test_list_passes_all_params(self) -> None:
        """Verify all optional parameters are forwarded when provided."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list(
                "dota2",
                conditions="[[name::Miracle-]]",
                query="name,id",
                limit=10,
                offset=5,
                order="name ASC",
                groupby="nationality",
            )

        params = _get_query_params(respx.calls.last.request)
        assert params["conditions"] == "[[name::Miracle-]]"
        assert params["query"] == "name,id"
        assert params["limit"] == "10"
        assert params["offset"] == "5"
        assert params["order"] == "name ASC"
        assert params["groupby"] == "nationality"

    @respx.mock
    def test_paginate_yields_records(self) -> None:
        """Verify paginate() yields individual records."""
        route = respx.get(f"{BASE_URL}player")
        route.side_effect = [
            httpx.Response(200, json={"result": [{"id": 1}, {"id": 2}]}),
            httpx.Response(200, json={"result": [{"id": 3}]}),
        ]

        with _make_client() as client:
            records = list(client.players.paginate("dota2", page_size=2))

        assert records == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert route.call_count == 2

    @respx.mock
    def test_paginate_excludes_none_params(self) -> None:
        """Verify paginate() excludes None-valued optional parameters."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            list(client.players.paginate("dota2"))

        params = _get_query_params(respx.calls.last.request)
        assert "conditions" not in params
        assert "order" not in params


# === Keyword Filters ===


class TestKeywordFilters:
    """Tests for keyword filter conversion to LPDB conditions."""

    @respx.mock
    def test_list_keyword_filter(self) -> None:
        """Verify a single keyword filter is converted to a condition."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("rocketleague", name="Zen")

        params = _get_query_params(respx.calls.last.request)
        assert params["conditions"] == "[[name::Zen]]"

    @respx.mock
    def test_list_multiple_filters(self) -> None:
        """Verify multiple keyword filters are AND-joined."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("rocketleague", name="Zen", nationality="fr")

        params = _get_query_params(respx.calls.last.request)
        assert "[[name::Zen]]" in params["conditions"]
        assert "[[nationality::fr]]" in params["conditions"]
        assert " AND " in params["conditions"]

    @respx.mock
    def test_list_filters_with_conditions(self) -> None:
        """Verify keyword filters are AND-joined with explicit conditions."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("rocketleague", conditions="[[team::Vitality]]", name="Zen")

        params = _get_query_params(respx.calls.last.request)
        assert "[[team::Vitality]]" in params["conditions"]
        assert "[[name::Zen]]" in params["conditions"]
        assert " AND " in params["conditions"]

    @respx.mock
    def test_list_filter_with_operator(self) -> None:
        """Verify operator prefixes in filter values are preserved."""
        respx.get(f"{BASE_URL}placement").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.placements.list("dota2", prizemoney=">10000")

        params = _get_query_params(respx.calls.last.request)
        assert params["conditions"] == "[[prizemoney::>10000]]"

    @respx.mock
    def test_list_no_filters_no_conditions(self) -> None:
        """Verify no conditions param is sent when neither filters nor conditions are provided."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.players.list("rocketleague")

        params = _get_query_params(respx.calls.last.request)
        assert "conditions" not in params

    @respx.mock
    def test_paginate_keyword_filter(self) -> None:
        """Verify keyword filters work with paginate()."""
        respx.get(f"{BASE_URL}player").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            list(client.players.paginate("rocketleague", name="Zen"))

        params = _get_query_params(respx.calls.last.request)
        assert params["conditions"] == "[[name::Zen]]"

    @respx.mock
    def test_match_filters_with_streams(self) -> None:
        """Verify keyword filters coexist with match-specific stream params."""
        respx.get(f"{BASE_URL}match").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.matches.list("rocketleague", rawstreams=True, winner="1")

        params = _get_query_params(respx.calls.last.request)
        assert params["conditions"] == "[[winner::1]]"
        assert params["rawstreams"] == "true"


# === Match Resource ===


class TestMatchResource:
    """Tests for the MatchResource with stream parameters."""

    @respx.mock
    def test_list_includes_rawstreams(self) -> None:
        """Verify rawstreams=True sends 'true' in params."""
        respx.get(f"{BASE_URL}match").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.matches.list("dota2", rawstreams=True)

        params = _get_query_params(respx.calls.last.request)
        assert params["rawstreams"] == "true"

    @respx.mock
    def test_list_includes_streamurls(self) -> None:
        """Verify streamurls=True sends 'true' in params."""
        respx.get(f"{BASE_URL}match").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.matches.list("dota2", streamurls=True)

        params = _get_query_params(respx.calls.last.request)
        assert params["streamurls"] == "true"

    @respx.mock
    def test_list_defaults_exclude_streams(self) -> None:
        """Verify stream parameters are excluded when False (default)."""
        respx.get(f"{BASE_URL}match").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.matches.list("dota2")

        params = _get_query_params(respx.calls.last.request)
        assert "rawstreams" not in params
        assert "streamurls" not in params

    @respx.mock
    def test_paginate_includes_stream_params(self) -> None:
        """Verify paginate() forwards stream parameters."""
        respx.get(f"{BASE_URL}match").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            list(client.matches.paginate("dota2", rawstreams=True, streamurls=True))

        params = _get_query_params(respx.calls.last.request)
        assert params["rawstreams"] == "true"
        assert params["streamurls"] == "true"


# === Team Template Resource ===


class TestTeamTemplateResource:
    """Tests for the TeamTemplateResource."""

    @respx.mock
    def test_get_sends_correct_endpoint(self) -> None:
        """Verify get() sends a GET to the teamtemplate endpoint."""
        route = respx.get(f"{BASE_URL}teamtemplate").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.team_templates.get("dota2", "teamliquid")

        assert route.called

    @respx.mock
    def test_get_sends_wiki_and_template(self) -> None:
        """Verify wiki and template parameters are sent."""
        respx.get(f"{BASE_URL}teamtemplate").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.team_templates.get("dota2", "teamliquid")

        params = _get_query_params(respx.calls.last.request)
        assert params["wiki"] == "dota2"
        assert params["template"] == "teamliquid"

    @respx.mock
    def test_get_optional_date(self) -> None:
        """Verify date parameter is forwarded when provided."""
        respx.get(f"{BASE_URL}teamtemplate").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.team_templates.get("dota2", "teamliquid", date="2009-06-05")

        params = _get_query_params(respx.calls.last.request)
        assert params["date"] == "2009-06-05"

    @respx.mock
    def test_get_excludes_date_when_none(self) -> None:
        """Verify date parameter is excluded when not provided."""
        respx.get(f"{BASE_URL}teamtemplate").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.team_templates.get("dota2", "teamliquid")

        params = _get_query_params(respx.calls.last.request)
        assert "date" not in params


# === Team Template List Resource ===


class TestTeamTemplateListResource:
    """Tests for the TeamTemplateListResource."""

    @respx.mock
    def test_list_sends_correct_endpoint(self) -> None:
        """Verify list() sends a GET to the teamtemplatelist endpoint."""
        route = respx.get(f"{BASE_URL}teamtemplatelist").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.team_template_list.list("dota2")

        assert route.called

    @respx.mock
    def test_list_with_pagination(self) -> None:
        """Verify pagination parameter is forwarded."""
        respx.get(f"{BASE_URL}teamtemplatelist").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.team_template_list.list("dota2", pagination=2)

        params = _get_query_params(respx.calls.last.request)
        assert params["pagination"] == "2"

    @respx.mock
    def test_list_excludes_pagination_when_none(self) -> None:
        """Verify pagination is excluded when not provided."""
        respx.get(f"{BASE_URL}teamtemplatelist").mock(return_value=httpx.Response(200, json={"result": []}))

        with _make_client() as client:
            client.team_template_list.list("dota2")

        params = _get_query_params(respx.calls.last.request)
        assert "pagination" not in params


# === Client Resource Attributes ===


class TestClientResourceAttributes:
    """Tests for resource attributes on LiquipediaClient."""

    @staticmethod
    def test_all_resources_attached() -> None:
        """Verify all 16 resource attributes exist and have the correct type."""
        with _make_client() as client:
            assert isinstance(client.broadcasters, BroadcastersResource)
            assert isinstance(client.companies, CompaniesResource)
            assert isinstance(client.datapoints, DatapointsResource)
            assert isinstance(client.external_media_links, ExternalMediaLinksResource)
            assert isinstance(client.matches, MatchResource)
            assert isinstance(client.placements, PlacementsResource)
            assert isinstance(client.players, PlayersResource)
            assert isinstance(client.series, SeriesResource)
            assert isinstance(client.squad_players, SquadPlayersResource)
            assert isinstance(client.standings_entries, StandingsEntriesResource)
            assert isinstance(client.standings_tables, StandingsTablesResource)
            assert isinstance(client.teams, TeamsResource)
            assert isinstance(client.tournaments, TournamentsResource)
            assert isinstance(client.transfers, TransfersResource)
            assert isinstance(client.team_templates, TeamTemplateResource)
            assert isinstance(client.team_template_list, TeamTemplateListResource)

    @staticmethod
    def test_resources_are_resource_subclasses() -> None:
        """Verify standard resources inherit from Resource."""
        with _make_client() as client:
            assert isinstance(client.players, Resource)
            assert isinstance(client.teams, Resource)
            assert isinstance(client.matches, Resource)

    @staticmethod
    def test_resource_endpoints() -> None:
        """Verify a few resources point to the correct endpoint strings."""
        with _make_client() as client:
            assert client.players._endpoint == "player"
            assert client.teams._endpoint == "team"
            assert client.broadcasters._endpoint == "broadcasters"
            assert client.matches._endpoint == "match"
            assert client.external_media_links._endpoint == "externalmedialink"

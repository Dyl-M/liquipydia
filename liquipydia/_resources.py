"""Resource classes for LPDB v3 endpoints."""

# Standard library
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

# Local
from liquipydia._models import (
    Broadcaster,
    Company,
    Datapoint,
    ExternalMediaLink,
    Match,
    Placement,
    Player,
    Series,
    SquadPlayer,
    StandingsEntry,
    StandingsTable,
    Team,
    Tournament,
    Transfer,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    # Third-party
    from pydantic import BaseModel

    # Local
    from liquipydia._client import LiquipediaClient
    from liquipydia._response import ApiResponse


# === Base Resource ===


class Resource:
    """Base resource wrapping a single LPDB v3 endpoint.

    Provides ``list`` and ``paginate`` methods that delegate HTTP calls to the parent client.
    Subclasses set ``_endpoint`` to the API path segment (e.g. ``"player"``) and ``_model``
    to the corresponding Pydantic model class for filter key validation.

    Args:
        client: The parent LiquipediaClient instance.
    """

    _endpoint: str
    _model: type[BaseModel]

    def __init__(self, client: LiquipediaClient) -> None:
        self._client = client

    def list(
        self,
        wiki: str,
        *,
        conditions: str | None = None,
        query: str | None = None,
        limit: int = 50,
        offset: int = 0,
        order: str | None = None,
        groupby: str | None = None,
        rawstreams: bool = False,
        streamurls: bool = False,
        **filters: str,
    ) -> ApiResponse:
        """Query this endpoint and return results.

        Args:
            wiki: Wiki(s) to query (pipe-separate for multi-wiki, e.g. ``"dota2|counterstrike"``).
            conditions: Filter expression using LPDB condition syntax.
            query: Comma-separated list of fields to return.
            limit: Maximum number of results (1--1000).
            offset: Number of results to skip.
            order: SQL-style ordering (e.g. ``"id ASC"``).
            groupby: SQL-style grouping (e.g. ``"id ASC"``).
            rawstreams: Return raw stream data (``/match`` endpoint only).
            streamurls: Return stream URLs (``/match`` endpoint only).
            **filters: Keyword filters converted to conditions (e.g. ``name="Zen"`` becomes
                ``[[name::Zen]]``). Prefix values with ``>``, ``<``, or ``!`` for operators.

        Returns:
            Parsed API response.
        """
        valid_fields = frozenset(self._model.model_fields)
        merged = self._build_conditions(conditions, filters, valid_fields)
        params = self._build_params(
            {
                "wiki": wiki,
                "conditions": merged,
                "query": query,
                "limit": limit,
                "offset": offset,
                "order": order,
                "groupby": groupby,
                "rawstreams": str(rawstreams).lower() if rawstreams else None,
                "streamurls": str(streamurls).lower() if streamurls else None,
            }
        )
        return self._client.get(self._endpoint, params)

    def paginate(
        self,
        wiki: str,
        *,
        conditions: str | None = None,
        query: str | None = None,
        order: str | None = None,
        groupby: str | None = None,
        rawstreams: bool = False,
        streamurls: bool = False,
        page_size: int = 50,
        max_results: int | None = None,
        **filters: str,
    ) -> Iterator[dict[str, Any]]:
        """Iterate through paginated results from this endpoint.

        Yields individual record dicts, automatically requesting successive pages.

        Args:
            wiki: Wiki(s) to query.
            conditions: Filter expression using LPDB condition syntax.
            query: Comma-separated list of fields to return.
            order: SQL-style ordering.
            groupby: SQL-style grouping.
            rawstreams: Return raw stream data (``/match`` endpoint only).
            streamurls: Return stream URLs (``/match`` endpoint only).
            page_size: Number of records per page (max 1000).
            max_results: Stop after yielding this many records. ``None`` for unlimited.
            **filters: Keyword filters converted to conditions (e.g. ``name="Zen"`` becomes
                ``[[name::Zen]]``). Prefix values with ``>``, ``<``, or ``!`` for operators.

        Yields:
            Individual record dicts from the API.
        """
        valid_fields = frozenset(self._model.model_fields)
        merged = self._build_conditions(conditions, filters, valid_fields)
        params = self._build_params(
            {
                "wiki": wiki,
                "conditions": merged,
                "query": query,
                "order": order,
                "groupby": groupby,
                "rawstreams": str(rawstreams).lower() if rawstreams else None,
                "streamurls": str(streamurls).lower() if streamurls else None,
            }
        )
        yield from self._client.paginate(
            self._endpoint,
            params,
            page_size=page_size,
            max_results=max_results,
        )

    @staticmethod
    def _build_conditions(
        conditions: str | None,
        filters: dict[str, str],
        valid_fields: frozenset[str] | None = None,
    ) -> str | None:
        """Merge an explicit conditions string with keyword filters.

        Each filter becomes ``[[key::value]]``. Filters are AND-joined with each other
        and with the explicit ``conditions`` string if provided. Values prefixed with
        ``>``, ``<``, or ``!`` preserve their LPDB operator.

        Args:
            conditions: Explicit LPDB condition string (can be ``None``).
            filters: Keyword filters to convert (e.g. ``{"name": "Zen"}``).
            valid_fields: Known model field names for validation. If provided, filter keys
                not in this set raise ``ValueError``.

        Returns:
            Merged condition string, or ``None`` if both inputs are empty.

        Raises:
            ValueError: If a filter key has invalid characters or is not a known model field.
        """
        valid_field = re.compile(r"[a-z_][a-z0-9_]*", re.IGNORECASE)

        parts: list[str] = []
        if conditions:
            parts.append(conditions)
        for key, value in filters.items():
            if not valid_field.fullmatch(key):
                raise ValueError(f"Invalid filter key: {key!r}")
            if valid_fields is not None and key not in valid_fields:
                raise ValueError(f"Unknown filter key {key!r} for this resource. Valid keys: {sorted(valid_fields)}")
            parts.append(f"[[{key}::{value}]]")
        return " AND ".join(parts) if parts else None

    @staticmethod
    def _build_params(raw: dict[str, Any]) -> dict[str, Any]:
        """Build a query parameter dict, excluding ``None`` values.

        Args:
            raw: Raw parameter mapping (may contain ``None`` values).

        Returns:
            Filtered parameter dict.
        """
        return {k: v for k, v in raw.items() if v is not None}


# === Standard Resources ===


class BroadcastersResource(Resource):
    """Resource for the ``/broadcasters`` endpoint."""

    _endpoint = "broadcasters"
    _model = Broadcaster


class CompaniesResource(Resource):
    """Resource for the ``/company`` endpoint."""

    _endpoint = "company"
    _model = Company


class DatapointsResource(Resource):
    """Resource for the ``/datapoint`` endpoint."""

    _endpoint = "datapoint"
    _model = Datapoint


class ExternalMediaLinksResource(Resource):
    """Resource for the ``/externalmedialink`` endpoint."""

    _endpoint = "externalmedialink"
    _model = ExternalMediaLink


class PlacementsResource(Resource):
    """Resource for the ``/placement`` endpoint."""

    _endpoint = "placement"
    _model = Placement


class PlayersResource(Resource):
    """Resource for the ``/player`` endpoint."""

    _endpoint = "player"
    _model = Player


class SeriesResource(Resource):
    """Resource for the ``/series`` endpoint."""

    _endpoint = "series"
    _model = Series


class SquadPlayersResource(Resource):
    """Resource for the ``/squadplayer`` endpoint."""

    _endpoint = "squadplayer"
    _model = SquadPlayer


class StandingsEntriesResource(Resource):
    """Resource for the ``/standingsentry`` endpoint."""

    _endpoint = "standingsentry"
    _model = StandingsEntry


class StandingsTablesResource(Resource):
    """Resource for the ``/standingstable`` endpoint."""

    _endpoint = "standingstable"
    _model = StandingsTable


class TeamsResource(Resource):
    """Resource for the ``/team`` endpoint."""

    _endpoint = "team"
    _model = Team


class TournamentsResource(Resource):
    """Resource for the ``/tournament`` endpoint."""

    _endpoint = "tournament"
    _model = Tournament


class TransfersResource(Resource):
    """Resource for the ``/transfer`` endpoint."""

    _endpoint = "transfer"
    _model = Transfer


# === Specialized Resources ===


class MatchResource(Resource):
    """Resource for the ``/match`` endpoint.

    Supports ``rawstreams`` and ``streamurls`` parameters via the base ``list()``
    and ``paginate()`` methods.
    """

    _endpoint = "match"
    _model = Match


class TeamTemplateResource:
    """Resource for the ``/teamtemplate`` endpoint (single template lookup).

    This endpoint has a different parameter signature from standard resources
    and does not support ``conditions``, ``limit``, ``offset``, or ``order``.

    Args:
        client: The parent LiquipediaClient instance.
    """

    def __init__(self, client: LiquipediaClient) -> None:
        self._client = client

    def get(
        self,
        wiki: str,
        template: str,
        *,
        date: str | None = None,
    ) -> ApiResponse:
        """Get a single team template.

        Args:
            wiki: Single wiki identifier (no multi-wiki).
            template: Template name of the team template (e.g. ``"teamliquid"``).
            date: Date for historical logos (format: ``YYYY-MM-DD``).

        Returns:
            Parsed API response.
        """
        params: dict[str, Any] = {"wiki": wiki, "template": template}
        if date is not None:
            params["date"] = date
        return self._client.get("teamtemplate", params)


class TeamTemplateListResource:
    """Resource for the ``/teamtemplatelist`` endpoint.

    This endpoint has a different parameter signature from standard resources
    and does not support ``conditions``, ``limit``, ``offset``, or ``order``.

    Args:
        client: The parent LiquipediaClient instance.
    """

    def __init__(self, client: LiquipediaClient) -> None:
        self._client = client

    def list(
        self,
        wiki: str,
        *,
        pagination: int | None = None,
    ) -> ApiResponse:
        """Get a list of team templates.

        Args:
            wiki: Single wiki identifier (no multi-wiki).
            pagination: Page number.

        Returns:
            Parsed API response.
        """
        params: dict[str, Any] = {"wiki": wiki}
        if pagination is not None:
            params["pagination"] = pagination
        return self._client.get("teamtemplatelist", params)

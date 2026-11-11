"""Resource classes for LPDB v3 endpoints."""

# Standard library
from __future__ import annotations

import datetime as dt
import re
from typing import TYPE_CHECKING, Any, get_args

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


# === Constants ===

# Functions LPDB accepts in a ``query`` item as ``function::field``; the result field is named ``function_field``.
# Aggregates apply to numerical columns, date extractors to date columns only (LPDB answers 404 otherwise).
_AGGREGATE_FUNCTIONS: frozenset[str] = frozenset({"count", "sum", "avg", "max", "min"})
_DATE_FUNCTIONS: frozenset[str] = frozenset({"year", "month", "day", "hour", "minute", "second"})
_QUERY_FUNCTIONS: frozenset[str] = _AGGREGATE_FUNCTIONS | _DATE_FUNCTIONS


# === Helpers ===


def _build_params(raw: dict[str, Any]) -> dict[str, Any]:
    """Build a query parameter dict, excluding ``None`` values.

    Args:
        raw: Raw parameter mapping (may contain ``None`` values).

    Returns:
        Filtered parameter dict.
    """
    return {k: v for k, v in raw.items() if v is not None}


def _is_date_type(annotation: object) -> bool:
    """Whether a model field annotation is a date or datetime, optional or not (e.g. ``dt.date | None``).

    Args:
        annotation: The field annotation, as stored by pydantic in ``FieldInfo.annotation``.

    Returns:
        True when the annotation, or one member of its union, is ``datetime.date`` or a subclass of it.
    """
    members = get_args(annotation) or (annotation,)
    return any(isinstance(member, type) and issubclass(member, dt.date) for member in members)


def _check_query_item(item: str, fields: frozenset[str], date_fields: frozenset[str]) -> None:
    """Check one stripped ``query`` item (``field`` or ``function::field``) against a model's fields.

    Args:
        item: The item, stripped of surrounding whitespace.
        fields: Field names of the resource's model (lowercase).
        date_fields: The subset of ``fields`` typed as dates or datetimes.

    Raises:
        ValueError: If the item is empty, uses an unknown function, names an unknown field, or applies a date function
            to a non-date field.
    """
    if not item:
        raise ValueError("Empty field in query (check for doubled or trailing commas)")
    function, separator, field = item.rpartition("::")
    function_key, field_key = function.lower(), field.lower()
    if separator and function_key not in _QUERY_FUNCTIONS:
        raise ValueError(
            f"Unknown query function {function!r} in {item!r}. Valid functions: {sorted(_QUERY_FUNCTIONS)}"
        )
    if field_key not in fields:
        raise ValueError(f"Unknown query field {field!r} for this resource. Valid fields: {sorted(fields)}")
    if function_key in _DATE_FUNCTIONS and field_key not in date_fields:
        raise ValueError(
            f"Date function {function!r} in {item!r} needs a date field. Date fields: {sorted(date_fields)}"
        )


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
            query: Comma-separated list of fields to return, each optionally wrapped in a function
                (e.g. ``"name,sum::earnings"``). Validated against the resource's model fields.
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

        Raises:
            ValueError: If a filter key or a ``query`` item is not valid for this resource (checked before any request).
        """
        valid_fields = frozenset(self._model.model_fields)
        self._validate_query(query)
        merged = self._build_conditions(conditions, filters, valid_fields)
        params = _build_params(
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
            query: Comma-separated list of fields to return, each optionally wrapped in a function
                (e.g. ``"name,sum::earnings"``). Validated against the resource's model fields.
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

        Raises:
            ValueError: If a filter key or a ``query`` item is not valid for this resource (checked before any request).
        """
        valid_fields = frozenset(self._model.model_fields)
        self._validate_query(query)
        merged = self._build_conditions(conditions, filters, valid_fields)
        params = _build_params(
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

    @classmethod
    def _validate_query(cls, query: str | None) -> None:
        """Check every item of a ``query`` string against the resource's model before it is sent.

        Items are comma-separated and stripped of surrounding whitespace for the check only (the string is sent
        unchanged). Each item is a model field, optionally prefixed by an LPDB function (``sum::prizemoney``). Field
        and function names are case-insensitive, as in LPDB. Without this check, LPDB answers an invalid item with
        HTTP 404, raised as a misleading ``NotFoundError``.

        Args:
            query: The ``query`` parameter; ``None`` or empty means all fields, with nothing to check.

        Raises:
            ValueError: If an item is empty, uses an unknown function, names a field the model does not have, or
                applies a date function to a non-date field.
        """
        if not query:
            return
        fields = cls._model.model_fields
        date_fields = frozenset(name for name, info in fields.items() if _is_date_type(info.annotation))
        for part in query.split(","):
            _check_query_item(part.strip(), frozenset(fields), date_fields)


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
        return self._client.get("teamtemplate", _build_params({"wiki": wiki, "template": template, "date": date}))


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
        return self._client.get("teamtemplatelist", _build_params({"wiki": wiki, "pagination": pagination}))

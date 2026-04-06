"""Pydantic models for LPDB v3 API response records."""

# Standard library
import datetime as dt
from typing import Annotated, Any

# Third-party
from pydantic import BaseModel, BeforeValidator, ConfigDict

# === Helpers ===

_NULL_DATE_PREFIX = "0000-01-01"


def _coerce_null_date(v: object) -> object:
    """Convert LPDB null-date sentinels to ``None``.

    The API uses ``"0000-01-01"`` and empty strings as placeholders for unknown dates.
    """
    if isinstance(v, str) and (not v or v.startswith(_NULL_DATE_PREFIX)):
        return None
    return v


def _coerce_empty_list_to_none(v: object) -> object:
    """Convert empty lists to ``None``.

    The API returns ``[]`` instead of ``{}`` or ``null`` for empty dict-like fields.
    """
    if isinstance(v, list) and len(v) == 0:
        return None
    return v


NullableDate = Annotated[dt.date | None, BeforeValidator(_coerce_null_date)]
"""A ``date`` field that converts LPDB null sentinels (``"0000-01-01"``, ``""``) to ``None``."""

NullableDatetime = Annotated[dt.datetime | None, BeforeValidator(_coerce_null_date)]
"""A ``datetime`` field that converts LPDB null sentinels (``"0000-01-01 00:00:00"``, ``""``) to ``None``."""

LpdbDict = Annotated[dict[str, Any] | None, BeforeValidator(_coerce_empty_list_to_none)]
"""A ``dict`` field that converts empty API lists (``[]``) to ``None``."""


# === Base Models ===


class _LpdbModel(BaseModel):
    """Base model for LPDB v3 response records.

    Provides common fields shared across most endpoints and allows extra fields
    since the API schema is not fully documented.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    pageid: int | None = None
    pagename: str | None = None
    namespace: int | None = None
    objectname: str | None = None
    wiki: str | None = None


class _TeamTemplateBase(BaseModel):
    """Base model for team template records.

    Team template endpoints return a different field set from standard endpoints
    (no ``pageid``, ``namespace``, ``objectname``, or ``wiki``).
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    template: str | None = None
    page: str | None = None
    name: str | None = None
    shortname: str | None = None
    bracketname: str | None = None
    image: str | None = None
    imagedark: str | None = None
    legacyimage: str | None = None
    legacyimagedark: str | None = None
    imageurl: str | None = None
    imagedarkurl: str | None = None
    legacyimageurl: str | None = None
    legacyimagedarkurl: str | None = None


# === Models ===


class Broadcaster(_LpdbModel):
    """A broadcaster record from the ``/broadcasters`` endpoint."""

    id: str | None = None
    name: str | None = None
    page: str | None = None
    position: str | None = None
    language: str | None = None
    flag: str | None = None
    weight: int | None = None
    date: NullableDate = None
    parent: str | None = None
    extradata: LpdbDict = None


class Company(_LpdbModel):
    """A company record from the ``/company`` endpoint."""

    name: str | None = None
    image: str | None = None
    imageurl: str | None = None
    imagedark: str | None = None
    imagedarkurl: str | None = None
    locations: LpdbDict = None
    parentcompany: str | None = None
    sistercompany: str | None = None
    industry: str | None = None
    foundeddate: NullableDatetime = None
    defunctdate: NullableDatetime = None
    defunctfate: str | None = None
    links: LpdbDict = None
    extradata: LpdbDict = None


class Datapoint(_LpdbModel):
    """A datapoint record from the ``/datapoint`` endpoint."""

    type: str | None = None
    name: str | None = None
    information: str | None = None
    image: str | None = None
    imageurl: str | None = None
    imagedark: str | None = None
    imagedarkurl: str | None = None
    date: NullableDatetime = None
    extradata: LpdbDict = None


class ExternalMediaLink(_LpdbModel):
    """An external media link record from the ``/externalmedialink`` endpoint."""

    title: str | None = None
    translatedtitle: str | None = None
    link: str | None = None
    date: NullableDate = None
    authors: LpdbDict = None
    language: str | None = None
    publisher: str | None = None
    type: str | None = None
    extradata: dict[str, Any] | list[Any] | None = None


class Match(_LpdbModel):
    """A match record from the ``/match`` endpoint."""

    match2id: str | None = None
    match2bracketid: str | None = None
    status: str | None = None
    winner: str | None = None
    walkover: str | None = None
    resulttype: str | None = None
    finished: int | None = None
    mode: str | None = None
    type: str | None = None
    section: str | None = None
    game: str | None = None
    patch: str | None = None
    date: NullableDatetime = None
    dateexact: int | None = None
    stream: dict[str, Any] | list[Any] | None = None
    links: LpdbDict = None
    bestof: int | None = None
    vod: str | None = None
    tournament: str | None = None
    parent: str | None = None
    tickername: str | None = None
    shortname: str | None = None
    series: str | None = None
    icon: str | None = None
    iconurl: str | None = None
    icondark: str | None = None
    icondarkurl: str | None = None
    liquipediatier: str | None = None
    liquipediatiertype: str | None = None
    publishertier: str | None = None
    extradata: LpdbDict = None
    match2bracketdata: LpdbDict = None
    match2opponents: list[Any] | None = None
    match2games: list[Any] | None = None


class Placement(_LpdbModel):
    """A placement record from the ``/placement`` endpoint."""

    tournament: str | None = None
    series: str | None = None
    parent: str | None = None
    imageurl: str | None = None
    imagedarkurl: str | None = None
    startdate: NullableDatetime = None
    date: NullableDatetime = None
    placement: str | None = None  # skipcq: PTC-W0052 — field name matches API response key
    prizemoney: int | None = None
    individualprizemoney: int | None = None
    prizepoolindex: int | None = None
    weight: float | None = None
    mode: str | None = None
    type: str | None = None
    liquipediatier: str | None = None
    liquipediatiertype: str | None = None
    publishertier: str | None = None
    icon: str | None = None
    iconurl: str | None = None
    icondark: str | None = None
    icondarkurl: str | None = None
    game: str | None = None
    lastvsdata: LpdbDict = None
    opponentname: str | None = None
    opponenttemplate: str | None = None
    opponenttype: str | None = None
    opponentplayers: LpdbDict = None
    qualifier: str | None = None
    qualifierpage: str | None = None
    qualifierurl: str | None = None
    extradata: LpdbDict = None


class Player(_LpdbModel):
    """A player record from the ``/player`` endpoint."""

    id: str | None = None
    alternateid: str | None = None
    name: str | None = None
    localizedname: str | None = None
    type: str | None = None
    nationality: str | None = None
    nationality2: str | None = None
    nationality3: str | None = None
    region: str | None = None
    birthdate: NullableDate = None
    deathdate: NullableDate = None
    teampagename: str | None = None
    teamtemplate: str | None = None
    links: LpdbDict = None
    status: str | None = None
    earnings: int | None = None
    earningsbyyear: dict[str, Any] | list[Any] | None = None
    extradata: LpdbDict = None


class Series(_LpdbModel):
    """A series record from the ``/series`` endpoint."""

    name: str | None = None
    abbreviation: str | None = None
    image: str | None = None
    imageurl: str | None = None
    imagedark: str | None = None
    imagedarkurl: str | None = None
    icon: str | None = None
    iconurl: str | None = None
    icondark: str | None = None
    icondarkurl: str | None = None
    game: str | None = None
    type: str | None = None
    organizers: LpdbDict = None
    locations: LpdbDict = None
    prizepool: float | None = None
    liquipediatier: str | None = None
    liquipediatiertype: str | None = None
    publishertier: str | None = None
    launcheddate: NullableDate = None
    defunctdate: NullableDate = None
    defunctfate: str | None = None
    links: LpdbDict = None
    extradata: LpdbDict = None


class SquadPlayer(_LpdbModel):
    """A squad player record from the ``/squadplayer`` endpoint."""

    id: str | None = None
    link: str | None = None
    name: str | None = None
    nationality: str | None = None
    position: str | None = None
    role: str | None = None
    type: str | None = None
    newteam: str | None = None
    teamtemplate: str | None = None
    newteamtemplate: str | None = None
    status: str | None = None
    joindate: NullableDate = None
    joindateref: str | None = None
    leavedate: NullableDate = None
    leavedateref: str | None = None
    inactivedate: NullableDate = None
    inactivedateref: str | None = None
    extradata: LpdbDict = None


class StandingsEntry(_LpdbModel):
    """A standings entry record from the ``/standingsentry`` endpoint."""

    parent: str | None = None
    standingsindex: int | None = None
    opponenttype: str | None = None
    opponentname: str | None = None
    opponenttemplate: str | None = None
    opponentplayers: LpdbDict = None
    placement: int | None = None
    definitestatus: str | None = None
    currentstatus: str | None = None
    placementchange: int | None = None
    scoreboard: LpdbDict = None
    roundindex: int | None = None
    slotindex: int | None = None
    extradata: LpdbDict = None


class StandingsTable(_LpdbModel):
    """A standings table record from the ``/standingstable`` endpoint."""

    parent: str | None = None
    standingsindex: int | None = None
    title: str | None = None
    tournament: str | None = None
    section: str | None = None
    type: str | None = None
    matches: dict[str, Any] | list[Any] | None = None
    config: dict[str, Any] | list[Any] | None = None
    extradata: LpdbDict = None


class Team(_LpdbModel):
    """A team record from the ``/team`` endpoint."""

    name: str | None = None
    locations: LpdbDict = None
    region: str | None = None
    logo: str | None = None
    logourl: str | None = None
    logodark: str | None = None
    logodarkurl: str | None = None
    textlesslogourl: str | None = None
    textlesslogodarkurl: str | None = None
    status: str | None = None
    createdate: NullableDate = None
    disbanddate: NullableDate = None
    earnings: int | None = None
    earningsbyyear: LpdbDict = None
    template: str | None = None
    links: LpdbDict = None
    extradata: LpdbDict = None


class Tournament(_LpdbModel):
    """A tournament record from the ``/tournament`` endpoint."""

    name: str | None = None
    shortname: str | None = None
    tickername: str | None = None
    banner: str | None = None
    bannerurl: str | None = None
    bannerdark: str | None = None
    bannerdarkurl: str | None = None
    icon: str | None = None
    iconurl: str | None = None
    icondark: str | None = None
    icondarkurl: str | None = None
    seriespage: str | None = None
    serieslist: LpdbDict = None
    previous: str | None = None
    previous2: str | None = None
    next: str | None = None
    next2: str | None = None
    game: str | None = None
    mode: str | None = None
    patch: str | None = None
    endpatch: str | None = None
    type: str | None = None
    organizers: str | None = None
    startdate: NullableDate = None
    enddate: NullableDate = None
    sortdate: NullableDate = None
    locations: LpdbDict = None
    prizepool: float | None = None
    participantsnumber: int | None = None
    liquipediatier: str | None = None
    liquipediatiertype: str | None = None
    publishertier: str | None = None
    status: str | None = None
    maps: str | None = None
    format: str | None = None
    sponsors: str | None = None
    extradata: LpdbDict = None


class Transfer(_LpdbModel):
    """A transfer record from the ``/transfer`` endpoint."""

    staticid: str | None = None
    player: str | None = None
    nationality: str | None = None
    fromteam: str | None = None
    toteam: str | None = None
    fromteamtemplate: str | None = None
    toteamtemplate: str | None = None
    role1: str | None = None
    role2: str | None = None
    reference: LpdbDict = None
    date: NullableDatetime = None
    wholeteam: int | None = None
    extradata: LpdbDict = None


# === Team Template Models ===


class TeamTemplate(_TeamTemplateBase):
    """A team template record from the ``/teamtemplate`` endpoint."""


class TeamTemplateList(_TeamTemplateBase):
    """A team template list record from the ``/teamtemplatelist`` endpoint."""

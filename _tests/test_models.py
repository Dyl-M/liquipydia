"""Tests for Pydantic models."""

# Standard library
import datetime as dt

# Third-party
from pydantic import BaseModel
import pytest

# Local
import liquipydia
from liquipydia import (
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
    TeamTemplate,
    TeamTemplateList,
    Tournament,
    Transfer,
)

# noinspection PyProtectedMember
from liquipydia._models import _LpdbModel, _TeamTemplateBase

# All 16 public model classes.
ALL_MODELS = [
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
    TeamTemplate,
    TeamTemplateList,
    Tournament,
    Transfer,
]


# === Base Model ===


class TestLpdbModel:
    """Tests for the _LpdbModel base class."""

    @staticmethod
    def test_accepts_common_fields() -> None:
        """Verify common fields are parsed correctly."""
        model = _LpdbModel.model_validate({"pageid": 123, "pagename": "Foo", "namespace": 0, "wiki": "dota2"})
        assert model.pageid == 123
        assert model.pagename == "Foo"
        assert model.namespace == 0
        assert model.wiki == "dota2"

    @staticmethod
    def test_all_fields_optional() -> None:
        """Verify the model can be constructed with no arguments."""
        model = _LpdbModel.model_validate({})
        assert model.pageid is None
        assert model.pagename is None

    @staticmethod
    def test_allows_extra_fields() -> None:
        """Verify unknown fields are preserved (extra='allow')."""
        model = _LpdbModel.model_validate({"pageid": 1, "unknown_field": "hello"})
        assert model.unknown_field == "hello"  # type: ignore[attr-defined]


# === All Models: Construction ===


class TestAllModelsConstruction:
    """Tests that apply to every model class."""

    @staticmethod
    @pytest.mark.parametrize("model_cls", ALL_MODELS, ids=lambda m: m.__name__)
    def test_empty_construction(model_cls: type) -> None:
        """Verify each model can be constructed with no arguments."""
        model = model_cls.model_validate({})
        assert model is not None

    @staticmethod
    @pytest.mark.parametrize("model_cls", ALL_MODELS, ids=lambda m: m.__name__)
    def test_allows_extra_fields(model_cls: type) -> None:
        """Verify each model accepts unknown fields."""
        model = model_cls.model_validate({"some_future_field": 42})
        assert model.some_future_field == 42  # type: ignore[attr-defined]


# === Empty List Coercion ===


class TestEmptyListCoercion:
    """Tests for empty list to None conversion on LpdbDict fields."""

    @staticmethod
    def test_empty_list_becomes_none() -> None:
        """Verify an empty list is converted to None for dict-like fields."""
        player = Player.model_validate({"links": []})
        assert player.links is None

    @staticmethod
    def test_dict_value_preserved() -> None:
        """Verify a real dict value is kept as-is."""
        player = Player.model_validate({"links": {"twitter": "https://twitter.com/test"}})
        assert player.links == {"twitter": "https://twitter.com/test"}

    @staticmethod
    def test_empty_dict_preserved() -> None:
        """Verify an empty dict is kept as-is (only empty lists are coerced)."""
        player = Player.model_validate({"links": {}})
        assert player.links == {}


# === Date Normalization ===


@pytest.mark.parametrize(
    ("model_cls", "field", "raw", "expected"),
    [
        # --- Null sentinels ---
        pytest.param(Player, "birthdate", "0000-01-01", None, id="null-date"),
        pytest.param(Player, "deathdate", "0000-01-01", None, id="null-date-other-field"),
        pytest.param(Company, "foundeddate", "0000-01-01 00:00:00", None, id="null-datetime"),
        pytest.param(Player, "birthdate", "", None, id="empty-string"),
        pytest.param(SquadPlayer, "leavedate", "0000-01-01", None, id="squadplayer-null-date"),
        pytest.param(SquadPlayer, "inactivedate", "", None, id="squadplayer-empty-string"),
        # --- Real values ---
        pytest.param(Player, "birthdate", "1995-02-14", dt.date(1995, 2, 14), id="valid-date"),
        pytest.param(Match, "date", "2019-04-27 15:46:00", dt.datetime(2019, 4, 27, 15, 46, 0), id="valid-datetime"),
        pytest.param(SquadPlayer, "joindate", "2019-05-01", dt.date(2019, 5, 1), id="squadplayer-valid-date"),
    ],
)
def test_date_normalization(model_cls: type[BaseModel], field: str, raw: str, expected: object) -> None:
    """Verify LPDB null-date sentinels become None and real dates / datetimes are parsed."""
    model = model_cls.model_validate({field: raw})
    assert getattr(model, field) == expected


# === Model-Specific Parsing ===

TEAM_TEMPLATE_SAMPLE: dict[str, object] = {
    "template": "teamliquid",
    "page": "TeamLiquid",
    "name": "TeamLiquid",
    "shortname": "TL",
    "bracketname": "TeamLiquid",
    "image": "TL_logo.png",
    "imageurl": "https://example.com/tl.png",
}
TEAM_TEMPLATE_EXPECTED: dict[str, object] = {
    "template": "teamliquid",
    "name": "TeamLiquid",
    "imageurl": "https://example.com/tl.png",
}


@pytest.mark.parametrize(
    ("model_cls", "sample", "expected"),
    [
        pytest.param(
            Player,
            {
                "pageid": 100007,
                "pagename": "Aonir",
                "namespace": 0,
                "objectname": "100007_staff_Aonir",
                "id": "Aonir",
                "alternateid": "",
                "name": "Carolin Hanisch",
                "type": "staff",
                "nationality": "Germany",
                "nationality2": "",
                "nationality3": "",
                "region": "Europe",
                "birthdate": "0000-01-01",
                "deathdate": "0000-01-01",
                "status": "Inactive",
                "earnings": 0,
                "earningsbyyear": [],
                "links": {"twitter": "https://twitter.com/Aon1r"},
                "extradata": {"role": "observer"},
                "wiki": "dota2",
            },
            {
                "id": "Aonir",
                "name": "Carolin Hanisch",
                "nationality": "Germany",
                "birthdate": None,
                "earnings": 0,
                "wiki": "dota2",
                "links": {"twitter": "https://twitter.com/Aon1r"},
            },
            id="Player",
        ),
        pytest.param(
            Team,
            {
                "pageid": 100223,
                "pagename": "Beastcoast",
                "name": "beastcoast",
                "region": "South America",
                "status": "disbanded",
                "createdate": "2017-07-02",
                "disbanddate": "2024-12-05",
                "earnings": 2079695,
                "earningsbyyear": {"2024": 290912, "2021": 674550},
                "template": "beastcoast",
                "links": {"twitter": "https://twitter.com/beastcoast"},
                "wiki": "dota2",
            },
            {
                "name": "beastcoast",
                "createdate": dt.date(2017, 7, 2),
                "disbanddate": dt.date(2024, 12, 5),
                "earnings": 2079695,
                "status": "disbanded",
            },
            id="Team",
        ),
        pytest.param(
            Match,
            {
                "pageid": 100012,
                "match2id": "vlvyfJG3PQ_R01-M001",
                "winner": "2",
                "finished": 1,
                "bestof": 1,
                "date": "2019-04-27 15:46:00",
                "dateexact": 1,
                "tournament": "Epulze Monthly Cup April 2019",
                "match2opponents": [{"name": "Team A"}, {"name": "Team B"}],
                "wiki": "dota2",
            },
            {
                "match2id": "vlvyfJG3PQ_R01-M001",
                "winner": "2",
                "finished": 1,
                "bestof": 1,
                "date": dt.datetime(2019, 4, 27, 15, 46, 0),
                "match2opponents": [{"name": "Team A"}, {"name": "Team B"}],
            },
            id="Match",
        ),
        pytest.param(
            Tournament,
            {
                "pageid": 100012,
                "name": "Epulze Monthly Cup April 2019",
                "startdate": "2019-04-27",
                "enddate": "2019-04-27",
                "prizepool": 500,
                "participantsnumber": 65,
                "liquipediatier": "4",
                "wiki": "dota2",
            },
            {
                "name": "Epulze Monthly Cup April 2019",
                "startdate": dt.date(2019, 4, 27),
                "prizepool": 500,
                "participantsnumber": 65,
            },
            id="Tournament",
        ),
        pytest.param(TeamTemplate, TEAM_TEMPLATE_SAMPLE, TEAM_TEMPLATE_EXPECTED, id="TeamTemplate"),
        pytest.param(TeamTemplateList, TEAM_TEMPLATE_SAMPLE, TEAM_TEMPLATE_EXPECTED, id="TeamTemplateList"),
    ],
)
def test_parses_sample(model_cls: type[BaseModel], sample: dict[str, object], expected: dict[str, object]) -> None:
    """Verify each model correctly parses a real API response dict."""
    model = model_cls.model_validate(sample)
    assert {field: getattr(model, field) for field in expected} == expected


# === Team Template Models ===


class TestTeamTemplateModels:
    """Tests for the TeamTemplate and TeamTemplateList class hierarchy."""

    @staticmethod
    def test_not_lpdb_model_subclass() -> None:
        """Verify team template models do not inherit from _LpdbModel."""
        assert not issubclass(TeamTemplate, _LpdbModel)
        assert not issubclass(TeamTemplateList, _LpdbModel)
        assert issubclass(TeamTemplate, _TeamTemplateBase)
        assert issubclass(TeamTemplateList, _TeamTemplateBase)

    @staticmethod
    def test_no_pageid_field() -> None:
        """Verify team template models do not have pageid or wiki as declared fields."""
        assert {"pageid", "wiki"}.isdisjoint(TeamTemplate.model_fields)


# === Exports ===


class TestExports:
    """Tests for model exports in __init__."""

    @staticmethod
    @pytest.mark.parametrize("model_cls", ALL_MODELS, ids=lambda m: m.__name__)
    def test_model_in_all(model_cls: type) -> None:
        """Verify each model is listed in __all__."""
        assert model_cls.__name__ in liquipydia.__all__

    @staticmethod
    def test_private_bases_not_in_all() -> None:
        """Verify private base classes are not in __all__."""
        assert {"_LpdbModel", "_TeamTemplateBase"}.isdisjoint(liquipydia.__all__)

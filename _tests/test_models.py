"""Tests for Pydantic models."""

# Standard library
import datetime as dt
from typing import ClassVar

# Third-party
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


# === Date Normalization ===


class TestDateNormalization:
    """Tests for null date sentinel conversion."""

    @staticmethod
    def test_null_date_becomes_none() -> None:
        """Verify '0000-01-01' is converted to None for date fields."""
        player = Player.model_validate({"birthdate": "0000-01-01"})
        assert player.birthdate is None

    @staticmethod
    def test_null_datetime_becomes_none() -> None:
        """Verify '0000-01-01 00:00:00' is converted to None for datetime fields."""
        company = Company.model_validate({"foundeddate": "0000-01-01 00:00:00"})
        assert company.foundeddate is None

    @staticmethod
    def test_empty_string_becomes_none() -> None:
        """Verify empty string is converted to None for date fields."""
        player = Player.model_validate({"birthdate": ""})
        assert player.birthdate is None

    @staticmethod
    def test_valid_date_parsed() -> None:
        """Verify a real date string is parsed to a date object."""
        player = Player.model_validate({"birthdate": "1995-02-14"})
        assert player.birthdate == dt.date(1995, 2, 14)

    @staticmethod
    def test_valid_datetime_parsed() -> None:
        """Verify a real datetime string is parsed to a datetime object."""
        match = Match.model_validate({"date": "2019-04-27 15:46:00"})
        assert match.date == dt.datetime(2019, 4, 27, 15, 46, 0)

    @staticmethod
    def test_multiple_date_fields() -> None:
        """Verify null date conversion works across multiple date fields."""
        player = Player.model_validate({"birthdate": "0000-01-01", "deathdate": "0000-01-01"})
        assert player.birthdate is None
        assert player.deathdate is None

    @staticmethod
    def test_squad_player_dates() -> None:
        """Verify SquadPlayer date fields are normalized correctly."""
        sp = SquadPlayer.model_validate(
            {
                "joindate": "2019-05-01",
                "leavedate": "0000-01-01",
                "inactivedate": "",
            }
        )
        assert sp.joindate == dt.date(2019, 5, 1)
        assert sp.leavedate is None
        assert sp.inactivedate is None


# === Model-Specific Parsing ===


class TestPlayerModel:
    """Tests for the Player model."""

    SAMPLE: ClassVar[dict[str, object]] = {
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
    }

    def test_parses_sample(self) -> None:
        """Verify Player correctly parses a real API response dict."""
        player = Player.model_validate(self.SAMPLE)
        assert player.id == "Aonir"
        assert player.name == "Carolin Hanisch"
        assert player.nationality == "Germany"
        assert player.birthdate is None
        assert player.earnings == 0
        assert player.wiki == "dota2"
        assert player.links == {"twitter": "https://twitter.com/Aon1r"}


class TestTeamModel:
    """Tests for the Team model."""

    SAMPLE: ClassVar[dict[str, object]] = {
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
    }

    def test_parses_sample(self) -> None:
        """Verify Team correctly parses a real API response dict."""
        team = Team.model_validate(self.SAMPLE)
        assert team.name == "beastcoast"
        assert team.createdate == dt.date(2017, 7, 2)
        assert team.disbanddate == dt.date(2024, 12, 5)
        assert team.earnings == 2079695
        assert team.status == "disbanded"


class TestMatchModel:
    """Tests for the Match model."""

    SAMPLE: ClassVar[dict[str, object]] = {
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
    }

    def test_parses_sample(self) -> None:
        """Verify Match correctly parses a real API response dict."""
        match = Match.model_validate(self.SAMPLE)
        assert match.match2id == "vlvyfJG3PQ_R01-M001"
        assert match.winner == "2"
        assert match.finished == 1
        assert match.bestof == 1
        assert match.date == dt.datetime(2019, 4, 27, 15, 46, 0)
        assert match.match2opponents == [{"name": "Team A"}, {"name": "Team B"}]


class TestTournamentModel:
    """Tests for the Tournament model."""

    SAMPLE: ClassVar[dict[str, object]] = {
        "pageid": 100012,
        "name": "Epulze Monthly Cup April 2019",
        "startdate": "2019-04-27",
        "enddate": "2019-04-27",
        "prizepool": 500,
        "participantsnumber": 65,
        "liquipediatier": "4",
        "wiki": "dota2",
    }

    def test_parses_sample(self) -> None:
        """Verify Tournament correctly parses a real API response dict."""
        tournament = Tournament.model_validate(self.SAMPLE)
        assert tournament.name == "Epulze Monthly Cup April 2019"
        assert tournament.startdate == dt.date(2019, 4, 27)
        assert tournament.prizepool == 500
        assert tournament.participantsnumber == 65


# === Team Template Models ===


class TestTeamTemplateModels:
    """Tests for TeamTemplate and TeamTemplateList models."""

    SAMPLE: ClassVar[dict[str, object]] = {
        "template": "teamliquid",
        "page": "TeamLiquid",
        "name": "TeamLiquid",
        "shortname": "TL",
        "bracketname": "TeamLiquid",
        "image": "TL_logo.png",
        "imageurl": "https://example.com/tl.png",
    }

    def test_team_template_parses(self) -> None:
        """Verify TeamTemplate correctly parses a sample dict."""
        tt = TeamTemplate.model_validate(self.SAMPLE)
        assert tt.template == "teamliquid"
        assert tt.name == "TeamLiquid"
        assert tt.imageurl == "https://example.com/tl.png"

    def test_team_template_list_parses(self) -> None:
        """Verify TeamTemplateList correctly parses a sample dict."""
        ttl = TeamTemplateList.model_validate(self.SAMPLE)
        assert ttl.template == "teamliquid"

    @staticmethod
    def test_not_lpdb_model_subclass() -> None:
        """Verify team template models do not inherit from _LpdbModel."""
        assert not issubclass(TeamTemplate, _LpdbModel)
        assert not issubclass(TeamTemplateList, _LpdbModel)
        assert issubclass(TeamTemplate, _TeamTemplateBase)
        assert issubclass(TeamTemplateList, _TeamTemplateBase)

    @staticmethod
    def test_no_pageid_field() -> None:
        """Verify team template models do not have pageid as a declared field."""
        assert "pageid" not in TeamTemplate.model_fields
        assert "wiki" not in TeamTemplate.model_fields


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
        assert "_LpdbModel" not in liquipydia.__all__
        assert "_TeamTemplateBase" not in liquipydia.__all__

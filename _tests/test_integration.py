"""Integration tests that hit the live Liquipedia API.

These tests are opt-in: they require a valid API key via the ``LPDB_API_KEY``
environment variable or the ``.tokens/tokens.json`` file (``repo_key`` field).
Tests are automatically skipped when no key is available.
"""

# Standard library
import json
import os
from pathlib import Path

# Third-party
import pytest

# Local
from liquipydia import (
    ApiResponse,
    LiquipediaClient,
    Match,
    Player,
    TeamTemplate,
    TeamTemplateList,
    Tournament,
)

# === Constants ===

_WIKI = "rocketleague"
_TOKENS_PATH = Path(__file__).resolve().parent.parent / ".tokens" / "tokens.json"


# === Helpers ===


def _resolve_api_key() -> str | None:
    """Resolve the API key from environment variable or local tokens file."""
    key = os.environ.get("LPDB_API_KEY")
    if key:
        return key

    if _TOKENS_PATH.is_file():
        tokens = json.loads(_TOKENS_PATH.read_text(encoding="utf-8"))
        return tokens.get("repo_key")

    return None


_API_KEY = _resolve_api_key()

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _API_KEY, reason="No API key (set LPDB_API_KEY or provide .tokens/tokens.json)"),
]


def _make_client() -> LiquipediaClient:
    """Create a client configured for integration testing."""
    assert _API_KEY is not None
    return LiquipediaClient("liquipydia-integration-tests", api_key=_API_KEY, timeout=30.0)


# === Tests ===


class TestIntegration:
    """Integration tests against the live Liquipedia API."""

    @staticmethod
    def test_players_list() -> None:
        """Standard resource list returns parseable results."""
        with _make_client() as client:
            response = client.players.list(_WIKI, limit=5)

        assert isinstance(response, ApiResponse)
        assert len(response.result) > 0

        for record in response.result:
            Player.model_validate(record)

    @staticmethod
    def test_tournaments_list() -> None:
        """Another standard resource returns parseable results."""
        with _make_client() as client:
            response = client.tournaments.list(_WIKI, limit=5)

        assert isinstance(response, ApiResponse)
        assert len(response.result) > 0

        for record in response.result:
            Tournament.model_validate(record)

    @staticmethod
    def test_matches_list() -> None:
        """Match resource returns parseable results."""
        with _make_client() as client:
            response = client.matches.list(_WIKI, limit=5)

        assert isinstance(response, ApiResponse)
        assert len(response.result) > 0

        for record in response.result:
            Match.model_validate(record)

    @staticmethod
    def test_matches_with_streams() -> None:
        """Match resource with rawstreams and streamurls parameters."""
        with _make_client() as client:
            response = client.matches.list(_WIKI, limit=5, rawstreams=True, streamurls=True)

        assert isinstance(response, ApiResponse)
        assert len(response.result) > 0

        for record in response.result:
            Match.model_validate(record)

    @staticmethod
    def test_team_template_get() -> None:
        """TeamTemplateResource.get() with different API signature."""
        with _make_client() as client:
            response = client.team_templates.get(_WIKI, "team liquid")

        assert isinstance(response, ApiResponse)
        records = [r for r in response.result if r is not None]
        assert len(records) > 0

        TeamTemplate.model_validate(records[0])

    @staticmethod
    def test_team_template_list() -> None:
        """TeamTemplateListResource.list() returns parseable results."""
        with _make_client() as client:
            response = client.team_template_list.list(_WIKI)

        assert isinstance(response, ApiResponse)
        records = [r for r in response.result if r is not None]
        assert len(records) > 0

        for record in records:
            TeamTemplateList.model_validate(record)

    @staticmethod
    def test_pagination() -> None:
        """Pagination yields the expected number of records."""
        with _make_client() as client:
            records = list(client.players.paginate(_WIKI, page_size=2, max_results=5))

        assert len(records) == 5

        for record in records:
            Player.model_validate(record)

    @staticmethod
    def test_keyword_filter() -> None:
        """Keyword filter narrows results."""
        with _make_client() as client:
            response = client.teams.list(_WIKI, pagename="Moist_Esports")

        assert isinstance(response, ApiResponse)
        assert len(response.result) > 0
        assert response.result[0]["pagename"] == "Moist_Esports"

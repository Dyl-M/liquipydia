# Roadmap

## v0.0.1 — Project scaffold

Set up the project structure, tooling, and CI before writing any library code.

- [x] `pyproject.toml` with `uv` as build backend, metadata, and dependency groups (`dev`, `test`, `docs`)
- [x] Core dependencies: `httpx`, `pydantic >= 2`
- [x] Dev dependencies: `pytest`, `respx`, `ruff`, `mypy`
- [x] `.python-version` → `3.12`
- [x] Package layout: `liquipydia/` (flat layout)
- [x] CI workflow: lint (`ruff`), type-check (`mypy`), tests (`pytest`) on push/PR
- [x] `CHANGELOG.md` (Keep a Changelog format)
- [x] README skeleton with badges, install instructions, and data-license notice (CC-BY-SA 3.0 for Liquipedia data)

## v0.0.2 — Core client (`_client.py`)

The foundation everything else depends on. Handles transport, auth, compliance with Liquipedia API constraints.

- [x] `LiquipediaClient` class wrapping `httpx.Client`
    - Constructor: `app_name` (required), `api_key` (optional, from param or env var `LIQUIPEDIA_API_KEY`)
    - Custom `User-Agent` header: `{app_name} (via liquipydia/{version})`
    - `Accept-Encoding: gzip` by default
    - Session reuse (single `httpx.Client` instance)
    - Context manager support (`with LiquipediaClient(...) as client:`)
- [x] Base URL configuration (`https://api.liquipedia.net/api/v3/`)
- [x] Rate limiting (truncated exponential backoff on 429, respects `Retry-After` header)
- [x] Error handling: map HTTP status codes to typed exceptions (`LiquipediaError`, `RateLimitError`, `AuthError`,
  `NotFoundError`, `ApiError`)
- [x] Pagination helper (`paginate()` generator using `offset` + `limit`)
- [x] Response envelope parsing (`ApiResponse` dataclass — extracts `result` and `warning` from API response)

## v0.0.3 — Resource layer (16 data types)

One resource class per LPDB data type, attached to the client as attributes. Each resource mirrors a single API
endpoint.

- [x] Base `Resource` class with shared logic (`list`, `paginate`)
- [x] Named subclass per standard endpoint (13 subclasses inheriting from `Resource`)
- [x] `MatchResource` subclass with extra `rawstreams` / `streamurls` parameters
- [x] `TeamTemplateResource` (standalone, uses `get()` — different API signature)
- [x] `TeamTemplateListResource` (standalone, uses `pagination` param)
- [x] Keyword filters: `**filters` kwargs on `list()` / `paginate()` auto-converted to LPDB conditions
  (e.g. `name="Zen"` becomes `[[name::Zen]]`, combinable with explicit `conditions`)
- [x] `client.broadcasters` — `/v3/broadcasters`
- [x] `client.companies` — `/v3/company`
- [x] `client.datapoints` — `/v3/datapoint`
- [x] `client.external_media_links` — `/v3/externalmedialink`
- [x] `client.matches` — `/v3/match`
- [x] `client.placements` — `/v3/placement`
- [x] `client.players` — `/v3/player`
- [x] `client.series` — `/v3/series`
- [x] `client.squad_players` — `/v3/squadplayer`
- [x] `client.standings_entries` — `/v3/standingsentry`
- [x] `client.standings_tables` — `/v3/standingstable`
- [x] `client.teams` — `/v3/team`
- [x] `client.tournaments` — `/v3/tournament`
- [x] `client.transfers` — `/v3/transfer`
- [x] `client.team_templates` — `/v3/teamtemplate`
- [x] `client.team_template_list` — `/v3/teamtemplatelist`

Each resource exposes:

```python
def list(
        self, wiki: str, *,
        conditions: str | None, query: str | None,
        limit: int = 50, offset: int = 0,
        order: str | None, groupby: str | None,
        rawstreams: bool = False, streamurls: bool = False,
        **filters: str,
) -> ApiResponse


def paginate(
        self, wiki: str, *,
        conditions: str | None, query: str | None,
        order: str | None, groupby: str | None,
        rawstreams: bool = False, streamurls: bool = False,
        page_size: int = 50, max_results: int | None,
        **filters: str,
) -> Iterator[dict]
```

- `rawstreams` / `streamurls` are only meaningful on the `/match` endpoint (ignored by others).
- `**filters` are keyword arguments auto-converted to LPDB conditions (e.g. `pagename="Zen"` → `[[pagename::Zen]]`).
  Supports `>`, `<`, `!` operator prefixes.
- Query parameter mapping follows the LPDB v3 API (wiki, conditions, limit, offset, order, groupby, etc.).

## v0.0.4 — Pydantic models

Typed response models for IDE autocompletion and validation. One model per data type.

- [x] 16 Pydantic models in `liquipydia/_models.py`: `Broadcaster`, `Company`, `Datapoint`, `ExternalMediaLink`,
  `Match`, `Placement`, `Player`, `Series`, `SquadPlayer`, `StandingsEntry`, `StandingsTable`, `Team`, `Tournament`,
  `Transfer`, `TeamTemplate`, `TeamTemplateList`
- [x] Private base classes: `_LpdbModel` (common fields for standard endpoints) and `_TeamTemplateBase` (different
  field set for team template endpoints)
- [x] All fields `type | None = None` — fully optional, forward-compatible
- [x] `ConfigDict(extra="allow", populate_by_name=True)` — unknown/future API fields preserved
- [x] Reusable type aliases via `Annotated` + `BeforeValidator`:
    - `NullableDate` — converts LPDB null sentinels (`"0000-01-01"`, `""`) to `None`
    - `NullableDatetime` — same for datetime fields (`"0000-01-01 00:00:00"`)
    - `LpdbDict` — converts empty API lists (`[]`) to `None` for dict-like fields
- [x] Standalone usage: `Model.model_validate(record)` on dicts from `ApiResponse.result`
- [x] Field schemas discovered via live API calls (API does not document per-endpoint schemas)
- [x] All 16 models re-exported from `__init__.py` and listed in `__all__`
- [x] Test suite in `_tests/test_models.py` covering construction, date normalization, model-specific parsing, and
  exports

## v0.0.5 — Tests and documentation

- [x] Unit tests for client (request building, headers, error handling) using `respx` to mock `httpx`
- [x] Unit tests for each resource (parameter construction, response parsing)
- [x] Unit tests for Pydantic models (validation, edge cases)
- [ ] Integration test suite (opt-in, requires real API key, skipped in CI by default)
- [ ] `mkdocs-material` documentation site
    - Getting started / quickstart
    - API reference (auto-generated from docstrings)
    - Examples per resource

## v0.1.0 — First public release

First PyPI release covering the full LPDB v3 surface.

- [ ] PyPI publish workflow (GitHub Actions, trusted publishing)
- [ ] `CHANGELOG.md` entry
- [ ] GitHub Release with notes

## Future / Out of scope for v1

- Async support (`AsyncLiquipediaClient` wrapping `httpx.AsyncClient`, async resource classes, `pytest-asyncio`)
- Query builder / fluent interface (`client.query("match").where(...).select(...)`) — evaluate after v1 based on usage
- Response caching layer (local TTL cache)
- CLI tool for quick queries
- Webhook support (subscribe to `edit`, `delete`, `move`, `purge` page events)
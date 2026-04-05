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

- [ ] Base `Resource` class with shared logic (`list`, `get_by_id` if applicable)
- [ ] `client.broadcasters` — `/v3/broadcasters`
- [ ] `client.companies` — `/v3/company`
- [ ] `client.datapoints` — `/v3/datapoint`
- [ ] `client.external_media_links` — `/v3/externalmedialink`
- [ ] `client.matches` — `/v3/match`
- [ ] `client.placements` — `/v3/placement`
- [ ] `client.players` — `/v3/player`
- [ ] `client.series` — `/v3/series`
- [ ] `client.squad_players` — `/v3/squadplayer`
- [ ] `client.standings_entries` — `/v3/standingsentry`
- [ ] `client.standings_tables` — `/v3/standingstable`
- [ ] `client.teams` — `/v3/team`
- [ ] `client.tournaments` — `/v3/tournament`
- [ ] `client.transfers` — `/v3/transfer`
- [ ] `client.team_templates` — `/v3/teamtemplate`
- [ ] `client.team_template_list` — `/v3/teamtemplatelist`

Each resource exposes at minimum:

```python
def list(self, wiki: str, *, conditions: str | None, limit: int = 50, offset: int = 0, order: str | None) -> list[Model]
```

Query parameter mapping follows the LPDB v3 API (wiki, conditions, limit, offset, order, etc.).

## v0.0.4 — Pydantic models

Typed response models for IDE autocompletion and validation. One model per data type.

- [ ] One model per data type: `Broadcaster`, `Company`, `Datapoint`, `ExternalMediaLink`, `Match`, `Placement`,
  `Player`, `Series`, `SquadPlayer`, `StandingsEntry`, `StandingsTable`, `Team`, `Tournament`, `Transfer`,
  `TeamTemplate`, `TeamTemplateList`
- [ ] Field mapping from API snake_case JSON → Python attributes
- [ ] Optional fields handled with `None` defaults
- [ ] Date/datetime parsing where applicable
- [ ] Decision: strict validation vs. permissive (`model_config = ConfigDict(extra="allow")`)

> **Note:** This phase depends on the full API field documentation. Models can start with known/common fields and expand
> later.

## v0.0.5 — Tests and documentation

- [ ] Unit tests for client (request building, headers, error handling) using `respx` to mock `httpx`
- [ ] Unit tests for each resource (parameter construction, response parsing)
- [ ] Unit tests for Pydantic models (validation, edge cases)
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
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.4] - 2026-04-06

### Added

- Pydantic models for all 16 LPDB v3 data types in `_models.py`: `Broadcaster`, `Company`, `Datapoint`,
  `ExternalMediaLink`, `Match`, `Placement`, `Player`, `Series`, `SquadPlayer`, `StandingsEntry`, `StandingsTable`,
  `Team`, `TeamTemplate`, `TeamTemplateList`, `Tournament`, `Transfer`
- Private base classes: `_LpdbModel` (common fields for standard endpoints) and `_TeamTemplateBase` (different field set
  for team template endpoints)
- Reusable type aliases via `Annotated` + `BeforeValidator`: `NullableDate`, `NullableDatetime`, `LpdbDict` for
  automatic conversion of LPDB null sentinels and empty dict placeholders
- Standalone model usage: `Model.model_validate(record)` on dicts from `ApiResponse.result`
- Typed Models section in README with usage examples and LPDB quirk handling notes
- Test suite for Pydantic models covering construction, date normalization, model-specific parsing, and exports

### Changed

- Bump version to 0.0.4
- Re-export all 16 models from `__init__.py` and add to `__all__`
- Update Quick Start examples in README to demonstrate model validation with typed field access
- Update roadmap with completed v0.0.4 items and checked off existing test milestones
- Refactor `dev` dependency group to include `test` group via `include-group` instead of duplicating packages

### Fixed

- Suppress false positive DeepSource warning on `Placement` model

## [0.0.3] - 2026-04-06

### Added

- Resource layer: base `Resource` class with `list()` and `paginate()` methods
- 13 standard resource subclasses (one per LPDB endpoint: player, team, tournament, etc.)
- `MatchResource` subclass with `rawstreams`/`streamurls` support (excluded from request when `False`)
- `TeamTemplateResource` standalone class with `get(wiki, template)` for single template lookups
- `TeamTemplateListResource` standalone class with `list(wiki, pagination)` for template listing
- Keyword filters (`**filters: str`) on `list()`/`paginate()` auto-converted to LPDB conditions
  (e.g. `name="Zen"` → `[[name::Zen]]`), AND-joined with explicit `conditions`
- Operator prefix support in keyword filters (`>`, `<`, `!`)
- `page_size` validation in `paginate()` raising `ValueError` if `< 1`
- All 16 resources attached as typed attributes on `LiquipediaClient`
- Available Resources table in README with all endpoints and notes
- Test suite for resource layer, keyword filters, and client resource attributes

### Changed

- Bump version to 0.0.3
- Rename `_get()` → `get()` on `LiquipediaClient` to allow cross-module access from resources
- Replace low-level Quick Start examples in README with resource-based usage
- Update roadmap with completed v0.0.3 items and full method signatures
- Re-export `Resource` and all 16 subclasses from `__init__.py`

## [0.0.2] - 2026-04-05

### Added

- `LiquipediaClient` class wrapping `httpx.Client` with context manager and explicit `close()` support
- API key resolution from constructor parameter or `LIQUIPEDIA_API_KEY` environment variable
- Automatic request headers: `User-Agent`, `Accept-Encoding: gzip`, `Authorization`
- `_get()` method with truncated exponential backoff on HTTP 429 (respects `Retry-After` header)
- `paginate()` public generator for automatic offset/limit iteration across API pages
- Response envelope parsing into `ApiResponse` frozen dataclass (result + warnings)
- Exception hierarchy: `LiquipediaError`, `AuthError`, `NotFoundError`, `RateLimitError`, `ApiError`
- HTTP status code mapping to typed exceptions (403, 404, 429, body-level errors)
- Test suite for client, exceptions, and response wrapper
- Quick start example in README with `_get()` and `paginate()` usage

### Changed

- Bump version to 0.0.2
- Update project structure in README to reflect new modules
- Check off v0.0.2 items in roadmap
- Document merge strategy and branch protection rules in CONTRIBUTING.md
- Disable `RUF022` ruff rule to preserve comment-grouped `__all__` entries
- Convert test methods without `self` usage to `@staticmethod`
- Add `skipcq: PY-W2000` to `__init__.py` re-exports (false positive: imports used via `__all__`)

## [0.0.1] - 2026-04-05

### Added

- Project scaffold: `pyproject.toml` with hatchling build system, exact-pinned dependencies, and tool config
- `liquipydia` package with version metadata and PEP 561 type marker
- CI pipeline: ruff lint/format, mypy type checking, pytest with coverage and DeepSource reporting
- CodeQL workflow for monthly Python security analysis
- License year auto-update workflow
- Issue templates for bug reports and feature requests
- Pull request template with validation checklist
- Dependabot config for monthly uv and GitHub Actions dependency updates
- `CONTRIBUTING.md` with branch strategy, naming conventions, and PR guidelines
- `SECURITY.md` with vulnerability reporting process and disclosure policy
- `README.md` with badges, API access section, installation instructions, and data license notice
- `_docs/ROADMAP.md` with versioned milestones (v0.0.1 → v0.1.0) and future scope
- `.deepsource.toml` for static analysis and test coverage reporting
- `.gitattributes` with LF line ending normalization
- `CHANGELOG.md` (this file)

### Fixed

- Downgrade `astral-sh/setup-uv` from v8 to v7 (v8 major tag does not exist)
- Enforce docstrings in test suite (remove pydocstyle exemption for `_tests/`)

[Unreleased]: https://github.com/Dyl-M/liquipydia/compare/v0.0.4...dev

[0.0.4]: https://github.com/Dyl-M/liquipydia/compare/v0.0.3...v0.0.4

[0.0.3]: https://github.com/Dyl-M/liquipydia/compare/v0.0.2...v0.0.3

[0.0.2]: https://github.com/Dyl-M/liquipydia/compare/v0.0.1...v0.0.2

[0.0.1]: https://github.com/Dyl-M/liquipydia/releases/tag/v0.0.1

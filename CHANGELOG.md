# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Automatic semantic release workflow (`.github/workflows/release.yml`) using `python-semantic-release` v9 — parses
  Conventional Commit prefixes to determine version bump, updates all version locations, creates GitHub Release
- `[tool.semantic_release]` configuration in `pyproject.toml` for version bumping, tagging, and release creation
- PyPI version badge in README (auto-updates via shields.io)
- Tests for malformed JSON and non-dict JSON API responses in `TestParseResponse`

### Changed

- Replace hardcoded version assertion in `test_version_value` with semver format regex check
- Replace relative file links with absolute GitHub URLs in README and CONTRIBUTING to fix broken links on PyPI
- Reformat README title heading
- Update roadmap: mark v0.1.0 GitHub Release as complete, add semantic release as post-release item, expand "Future"
  section with HTTP client dependency evaluation

## [0.1.0] - 2026-04-11

### Added

- PyPI publish workflow (`.github/workflows/publish.yml`) using GitHub Actions trusted publishing (OIDC) — triggers on
  GitHub Release creation
- Documentation URL in `pyproject.toml` project metadata
- Filter key validation on `Resource.list()` and `Resource.paginate()` — unknown keys raise `ValueError` with the list
  of valid fields, validated against each resource's Pydantic model
- "Development Commands" section in `CONTRIBUTING.md` with lint, format, type check, test, coverage, and docs commands

### Changed

- Bump version to 0.1.0 — first public PyPI release
- Update development status classifier from "Planning" to "Beta"
- Update installation instructions in README and Sphinx docs to use PyPI (`pip install liquipydia`)
- Update README status badge and label from "early development" to "beta"

### Fixed

- Harden response parsing and retry backoff logic in `LiquipediaClient`
- Validate filter key format with regex before checking against model fields
- Add rate limit delay (10s) between integration tests to prevent API throttling in CI

## [0.0.5] - 2026-04-10

### Added

- Integration test suite in `_tests/test_integration.py` with `@pytest.mark.integration` marker (auto-skips when no
  API key is available; resolves key from `LPDB_API_KEY` env var or `.tokens/tokens.json`)
- Sphinx + Furo documentation site in `_docs/sphinx/` with Liquipedia-themed colors, autodoc API reference,
  getting-started guide, examples with output blocks, and changelog page
- Jinja2 template override for clickable author name in Furo footer
- GitHub Pages deployment workflow (`.github/workflows/docs.yml`, triggers on push to `main`)
- `LPDB_API_KEY` secret as env var in CI test job for integration tests
- Sphinx copyright year update step in license workflow (renamed to "Update License & Copyright years")
- Documentation section in README linking to GitHub Pages site
- Output blocks (`text` code fences) to code examples in README, getting-started, examples, and index pages
- Post-release section in roadmap with conda-forge package goal

### Changed

- Bump version to 0.0.5
- Switch documentation dependencies from mkdocs-material + mkdocstrings to Sphinx 9 + Furo + myst-parser +
  sphinx-autodoc-typehints + sphinx-copybutton + sphinx-autobuild
- Update roadmap with completed v0.0.5 items

### Fixed

- Remove incorrect `endpoint` parameter from `Resource` class docstring `Args:` section

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

[Unreleased]: https://github.com/Dyl-M/liquipydia/compare/v0.1.0...dev

[0.1.0]: https://github.com/Dyl-M/liquipydia/compare/v0.0.5...v0.1.0

[0.0.5]: https://github.com/Dyl-M/liquipydia/compare/v0.0.4...v0.0.5

[0.0.4]: https://github.com/Dyl-M/liquipydia/compare/v0.0.3...v0.0.4

[0.0.3]: https://github.com/Dyl-M/liquipydia/compare/v0.0.2...v0.0.3

[0.0.2]: https://github.com/Dyl-M/liquipydia/compare/v0.0.1...v0.0.2

[0.0.1]: https://github.com/Dyl-M/liquipydia/releases/tag/v0.0.1

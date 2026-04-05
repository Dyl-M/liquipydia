# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/Dyl-M/liquipydia/compare/v0.0.1...dev

[0.0.1]: https://github.com/Dyl-M/liquipydia/releases/tag/v0.0.1

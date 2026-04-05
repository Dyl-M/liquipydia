# liquipydia

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![License](https://img.shields.io/github/license/Dyl-M/liquipydia)

![Status](https://img.shields.io/badge/status-early%20development-orange?style=flat-square)
[![Lint & Test](https://img.shields.io/github/actions/workflow/status/Dyl-M/liquipydia/lint-and-test.yml?label=Lint%20%26%20Test&style=flat-square&logo=github-actions&logoColor=white)](https://github.com/Dyl-M/liquipydia/actions/workflows/lint-and-test.yml)
[![DeepSource](https://app.deepsource.com/gh/Dyl-M/liquipydia.svg/?label=active+issues&show_trend=true&token=TOKEN)](https://app.deepsource.com/gh/Dyl-M/liquipydia/)
[![DeepSource](https://app.deepsource.com/gh/Dyl-M/liquipydia.svg/?label=code+coverage&show_trend=true&token=TOKEN)](https://app.deepsource.com/gh/Dyl-M/liquipydia/)

Python client library for the [Liquipedia](https://liquipedia.net/) API (LPDB v3).

## About

**liquipydia** aims to be a modern, typed Python wrapper for the Liquipedia Database (LPDB) REST API v3, covering all
16 data types (matches, tournaments, teams, players, transfers, and more).

Built with [`httpx`](https://www.python-httpx.org/) and [`pydantic`](https://docs.pydantic.dev/).

> **Status:** Early development — see the [Roadmap](_docs/ROADMAP.md) for progress.

## Project Structure

```
liquipydia/
├── __init__.py     # Package exports, version
└── py.typed        # PEP 561 type marker
```

## API Access

Using this library requires an API key from Liquipedia. Access is **not self-service** — you must request it through
their [contact form](https://liquipedia.net/api).

Free access is available for **educational**, **non-commercial open-source**, and **community** projects.
Paid plans (Basic, Premium, Enterprise) are available for commercial use.

## Installation

> **Note:** Not yet published on PyPI. Install from source for now.

```bash
# With uv (recommended)
uv add git+https://github.com/Dyl-M/liquipydia.git

# With pip
pip install git+https://github.com/Dyl-M/liquipydia.git
```

## Quick Start

```python
# Coming soon — see the Roadmap for progress.
```

## Development

```bash
# Clone the repository
git clone https://github.com/Dyl-M/liquipydia.git
cd liquipydia

# Install dependencies (requires uv)
uv sync --group dev

# Run linting
uv run ruff check .
uv run ruff format --check .

# Run type checking
uv run mypy liquipydia

# Run tests
uv run pytest
```

## License

Code is licensed under the [MIT License](LICENSE).

## Data License

Data returned by the Liquipedia API is subject to
[CC-BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) as required by Liquipedia's
[API Terms of Use](https://liquipedia.net/api-terms-of-use). If you redistribute or display data obtained
through this library, you must comply with the CC-BY-SA 3.0 attribution requirements.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

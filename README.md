# LIQUIPYDIA | Python client library for [Liquipedia](https://liquipedia.net/) API (LPDB v3)

[![PyPI](https://img.shields.io/pypi/v/liquipydia?logo=pypi&logoColor=white)](https://pypi.org/project/liquipydia/)
![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![License](https://img.shields.io/github/license/Dyl-M/liquipydia)

![Status](https://img.shields.io/badge/status-beta-green?style=flat-square)
[![Lint & Test](https://img.shields.io/github/actions/workflow/status/Dyl-M/liquipydia/lint-and-test.yml?label=Lint%20%26%20Test&style=flat-square&logo=github-actions&logoColor=white)](https://github.com/Dyl-M/liquipydia/actions/workflows/lint-and-test.yml)
[![DeepSource](https://app.deepsource.com/gh/Dyl-M/liquipydia.svg/?label=active+issues&show_trend=true&token=TOKEN)](https://app.deepsource.com/gh/Dyl-M/liquipydia/)
[![DeepSource](https://app.deepsource.com/gh/Dyl-M/liquipydia.svg/?label=code+coverage&show_trend=true&token=TOKEN)](https://app.deepsource.com/gh/Dyl-M/liquipydia/)

## About

**`liquipydia`** aims to be a modern, typed Python wrapper for the Liquipedia Database (LPDB) REST API v3, covering all
16 data types (matches, tournaments, teams, players, transfers, and more).

Built with [`httpx`](https://www.python-httpx.org/) and [`pydantic`](https://docs.pydantic.dev/).

> **Status:** Beta — see the [Roadmap](https://github.com/Dyl-M/liquipydia/blob/main/_docs/ROADMAP.md) for progress.

## Project Structure

```
liquipydia/
├── __init__.py       # Package exports, version
├── _client.py        # Core HTTP client (LiquipediaClient)
├── _models.py        # Pydantic models (one per LPDB data type)
├── _resources.py     # Resource classes (one per LPDB data type)
├── _exceptions.py    # Exception hierarchy
├── _response.py      # API response wrapper
└── py.typed          # PEP 561 type marker
```

## API Access

Using this library requires an API key from Liquipedia. Access is **not self-service** — you must request it through
their [contact form](https://liquipedia.net/api).

Free access is available for **educational**, **non-commercial open-source**, and **community** projects.
Paid plans (Basic, Premium, Enterprise) are available for commercial use.

## Installation

```bash
# With uv (recommended)
uv add liquipydia

# With pip
pip install liquipydia
```

Or install from source:

```bash
# With uv
uv add git+https://github.com/Dyl-M/liquipydia.git

# With pip
pip install git+https://github.com/Dyl-M/liquipydia.git
```

## Quick Start

```python
from liquipydia import LiquipediaClient, Player, Match

with LiquipediaClient("my-app", api_key="your-api-key") as client:
    # Query players from a specific wiki
    response = client.players.list("dota2", conditions="[[name::Miracle-]]")
    for record in response.result:
        player = Player.model_validate(record)
        print(player.name, player.nationality, player.birthdate)

    # Automatic pagination across multiple pages
    for record in client.matches.paginate("counterstrike", page_size=100, max_results=500):
        match = Match.model_validate(record)
        print(match.match2id, match.date, match.winner)

    # Keyword filters — no need to write raw LPDB conditions
    response = client.players.list("rocketleague", pagename="Zen")

    # Match-specific parameters (stream data)
    response = client.matches.list("rocketleague", rawstreams=True, streamurls=True)

    # Team template lookup
    response = client.team_templates.get("dota2", "teamliquid")
```

```text
Miracle- Jordan 1997-06-20
0042_R01-M001 2025-06-15 14:00:00 1
...
```

### Available Resources

All 16 LPDB v3 data types are accessible as client attributes:

| Attribute                     | Endpoint             | Notes                             |
|-------------------------------|----------------------|-----------------------------------|
| `client.broadcasters`         | `/broadcasters`      |                                   |
| `client.companies`            | `/company`           |                                   |
| `client.datapoints`           | `/datapoint`         |                                   |
| `client.external_media_links` | `/externalmedialink` |                                   |
| `client.matches`              | `/match`             | Extra: `rawstreams`, `streamurls` |
| `client.placements`           | `/placement`         |                                   |
| `client.players`              | `/player`            |                                   |
| `client.series`               | `/series`            |                                   |
| `client.squad_players`        | `/squadplayer`       |                                   |
| `client.standings_entries`    | `/standingsentry`    |                                   |
| `client.standings_tables`     | `/standingstable`    |                                   |
| `client.teams`                | `/team`              |                                   |
| `client.tournaments`          | `/tournament`        |                                   |
| `client.transfers`            | `/transfer`          |                                   |
| `client.team_templates`       | `/teamtemplate`      | Uses `get()` instead of `list()`  |
| `client.team_template_list`   | `/teamtemplatelist`  | Different params (`pagination`)   |

> The API key can also be set via the `LIQUIPEDIA_API_KEY` environment variable.

### Typed Models

Each data type has a corresponding Pydantic model for typed access and IDE autocompletion:

`Broadcaster`, `Company`, `Datapoint`, `ExternalMediaLink`, `Match`, `Placement`, `Player`, `Series`, `SquadPlayer`,
`StandingsEntry`, `StandingsTable`, `Team`, `TeamTemplate`, `TeamTemplateList`, `Tournament`, `Transfer`

```python
from liquipydia import Player

player = Player.model_validate(record)
print(player.name)  # str | None — with autocompletion
print(player.birthdate)  # date | None — null sentinels auto-converted
print(player.links)  # dict | None — empty API lists auto-converted
```

```text
Miracle-
1997-06-20
{'twitter': 'https://twitter.com/Aborss', ...}
```

Models handle LPDB quirks automatically:

- Null date sentinels (`"0000-01-01"`, `""`) → `None`
- Empty dict placeholders (`[]`) → `None`
- Unknown/future API fields are preserved (`extra="allow"`)

## Documentation

Full documentation (getting started, examples, API reference) is available at
**[dyl-m.github.io/liquipydia](https://dyl-m.github.io/liquipydia/)**.

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

Code is licensed under the [MIT License](https://github.com/Dyl-M/liquipydia/blob/main/LICENSE).

## Data License

Data returned by the Liquipedia API is subject to
[CC-BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) as required by Liquipedia's
[API Terms of Use](https://liquipedia.net/api-terms-of-use). If you redistribute or display data obtained
through this library, you must comply with the CC-BY-SA 3.0 attribution requirements.

## Contributing

See [CONTRIBUTING.md](https://github.com/Dyl-M/liquipydia/blob/main/CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](https://github.com/Dyl-M/liquipydia/blob/main/SECURITY.md) for reporting vulnerabilities.

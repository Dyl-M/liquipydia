# Getting Started

## API access

Using this library requires an API key from Liquipedia. Access is **not self-service** — you must request it through
their [contact form](https://liquipedia.net/api).

Free access is available for **educational**, **non-commercial open-source**, and **community** projects.
Paid plans (Basic, Premium, Enterprise) are available for commercial use.

## Installation

```{note}
Not yet published on PyPI. Install from source for now.
```

With uv (recommended):

```bash
uv add git+https://github.com/Dyl-M/liquipydia.git
```

With pip:

```bash
pip install git+https://github.com/Dyl-M/liquipydia.git
```

## Authentication

Pass your API key directly or set it as an environment variable:

```python
from liquipydia import LiquipediaClient

# Option 1: pass directly
client = LiquipediaClient("my-app", api_key="your-api-key")

# Option 2: environment variable
# export LIQUIPEDIA_API_KEY=your-api-key
client = LiquipediaClient("my-app")
```

## Quickstart

```python
from liquipydia import LiquipediaClient, Player, Match

with LiquipediaClient("my-app", api_key="your-api-key") as client:
    # Query players from a specific wiki
    response = client.players.list("dota2", pagename="Miracle-")
    for record in response.result:
        player = Player.model_validate(record)
        print(player.name, player.nationality, player.birthdate)

    # Automatic pagination across multiple pages
    for record in client.matches.paginate("counterstrike", page_size=100, max_results=500):
        match = Match.model_validate(record)
        print(match.match2id, match.date, match.winner)

    # Keyword filters — no need to write raw LPDB conditions
    response = client.players.list("rocketleague", pagename="Zen")

    # Team template lookup
    response = client.team_templates.get("dota2", "teamliquid")
```

```text
Miracle- Jordan 1997-06-20
0042_R01-M001 2025-06-15 14:00:00 1
...
```

## Available resources

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

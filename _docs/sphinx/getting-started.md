# Getting Started

## API access

Using this library requires an API key from Liquipedia. Access is **not self-service** — you must
request it through their [contact form](https://liquipedia.net/api).

Free access is available for **educational**, **non-commercial open-source**, and **community**
projects. Paid plans (Basic, Premium, Enterprise) are available for commercial use.

## Installation

With uv (recommended):

```bash
uv add liquipydia
```

With pip:

```bash
pip install liquipydia
```

Or install from source:

```bash
# With uv
uv add git+https://github.com/Dyl-M/liquipydia.git

# With pip
pip install git+https://github.com/Dyl-M/liquipydia.git
```

## Authentication

Pass your API key directly or set it as an environment variable:

```python
from liquipydia import LiquipediaClient

# Option 1: pass directly
client = LiquipediaClient("my-app", api_key="your-api-key")

# Option 2: read from LIQUIPEDIA_API_KEY env var
client = LiquipediaClient("my-app")
```

The first positional argument is the **application name**. It is included in the `User-Agent`
header of every request, alongside the library version, so Liquipedia operators can identify
traffic from your project.

## Quickstart

```python
from liquipydia import LiquipediaClient, Player, Tournament

with LiquipediaClient("my-app", api_key="your-api-key") as client:
    # Single query: top earners on the Dota 2 wiki
    response = client.players.list("dota2", order="earnings DESC", limit=5)
    for record in response.result:
        player = Player.model_validate(record)
        print(player.id, player.nationality, player.earnings)

    # Automatic pagination — iterate Tier-1 Dota 2 tournaments page by page
    for record in client.tournaments.paginate(
        "dota2",
        liquipediatier="1",
        order="startdate DESC",
        page_size=50,
        max_results=200,
    ):
        tournament = Tournament.model_validate(record)
        print(tournament.name, tournament.startdate)

    # Single team-template lookup (different signature — uses get())
    response = client.team_templates.get("dota2", "teamliquid")
```

See {doc}`examples` for queries with conditions, multi-wiki, stream metadata, error handling, and
more.

## Tuning

`LiquipediaClient` accepts a few keyword arguments to tune HTTP behaviour:

```python
client = LiquipediaClient(
    "my-app",
    api_key="your-api-key",
    timeout=30.0,             # per-request timeout (seconds)
    max_retries=3,            # retries on HTTP 429 before raising RateLimitError
    retry_backoff_factor=1.0, # base for exponential backoff between retries
)
```

The retry loop honours the API's `Retry-After` header when present and otherwise uses exponential
backoff capped at 60 seconds. Set `max_retries=0` to disable automatic retrying and let your code
handle `RateLimitError` directly.

## Available resources

All 16 LPDB v3 data types are accessible as client attributes:

| Attribute                     | Endpoint             | Notes                                         |
|-------------------------------|----------------------|-----------------------------------------------|
| `client.broadcasters`         | `/broadcasters`      |                                               |
| `client.companies`            | `/company`           |                                               |
| `client.datapoints`           | `/datapoint`         |                                               |
| `client.external_media_links` | `/externalmedialink` |                                               |
| `client.matches`              | `/match`             | Extra: `rawstreams`, `streamurls`             |
| `client.placements`           | `/placement`         |                                               |
| `client.players`              | `/player`            |                                               |
| `client.series`               | `/series`            |                                               |
| `client.squad_players`        | `/squadplayer`       |                                               |
| `client.standings_entries`    | `/standingsentry`    |                                               |
| `client.standings_tables`     | `/standingstable`    |                                               |
| `client.teams`                | `/team`              |                                               |
| `client.tournaments`          | `/tournament`        |                                               |
| `client.transfers`            | `/transfer`          |                                               |
| `client.team_templates`       | `/teamtemplate`      | `get(wiki, template, date=...)` — single wiki |
| `client.team_template_list`   | `/teamtemplatelist`  | Page-based via `pagination=N` — single wiki   |

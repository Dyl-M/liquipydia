# Examples

All examples assume you have a `LiquipediaClient` instance:

```python
from liquipydia import LiquipediaClient

client = LiquipediaClient("my-app", api_key="your-api-key")
```

```{tip}
Use the client as a context manager to ensure the HTTP session is properly closed:

    with LiquipediaClient("my-app", api_key="your-api-key") as client:
        ...
```

## Standard resources

Most resources share the same `list()` and `paginate()` interface. Here are some examples using
`players`, but the same pattern applies to `broadcasters`, `companies`, `datapoints`,
`external_media_links`, `placements`, `series`, `squad_players`, `standings_entries`,
`standings_tables`, `teams`, `tournaments`, and `transfers`.

### Basic query

```python
from liquipydia import Player

response = client.players.list("dota2", limit=10)

for record in response.result:
    player = Player.model_validate(record)
    print(player.name, player.nationality)
```

```text
Miracle- Jordan
SumaiL Pakistan
...
```

### LPDB conditions

```python
response = client.players.list(
    "counterstrike",
    conditions="[[nationality::Denmark]] AND [[status::Active]]",
    limit=20,
)
```

### Keyword filters

Instead of writing raw LPDB condition strings, use keyword arguments:

```python
# Simple equality
response = client.players.list("rocketleague", pagename="Zen")

# Operator prefixes: > (greater), < (less), ! (not)
response = client.tournaments.list("dota2", liquipediatier="1", prizepool=">100000")
```

Keyword filters can be combined with explicit `conditions`:

```python
response = client.players.list(
    "counterstrike",
    conditions="[[status::Active]]",
    nationality="Denmark",
)
```

### Selecting fields

Use the `query` parameter to return only specific fields:

```python
response = client.players.list("dota2", query="pagename,name,nationality", limit=5)
```

### Ordering and grouping

```python
response = client.tournaments.list("dota2", order="startdate DESC", limit=10)
```

### Multi-wiki queries

Pipe-separate wiki names to query across multiple games:

```python
response = client.players.list("dota2|counterstrike", limit=10)
```

## Pagination

The `paginate()` method handles offset management automatically, yielding individual records:

```python
from liquipydia import Match

# Get up to 500 matches, 100 per page
for record in client.matches.paginate("counterstrike", page_size=100, max_results=500):
    match = Match.model_validate(record)
    print(match.match2id, match.date)
```

```text
0042_R01-M001 2025-06-15 14:00:00
0042_R01-M002 2025-06-15 15:30:00
...
```

Without `max_results`, pagination continues until no more results are returned:

```python
# Iterate through ALL players (use with caution)
for record in client.players.paginate("rocketleague", page_size=200):
    player = Player.model_validate(record)
    print(player.name)
```

```text
Zen
Vatira
...
```

## Matches (stream data)

The match resource supports two extra parameters for stream data:

```python
from liquipydia import Match

response = client.matches.list(
    "rocketleague",
    rawstreams=True,
    streamurls=True,
    limit=5,
)

for record in response.result:
    match = Match.model_validate(record)
    print(match.match2id, match.stream)
```

```text
0001_R01-M001 {'twitch': 'rocketleague', 'youtube': '...'}
0001_R01-M002 {'twitch': 'rocketleague'}
...
```

These parameters also work with `paginate()`:

```python
for record in client.matches.paginate("dota2", rawstreams=True, max_results=50):
    match = Match.model_validate(record)
    print(match.match2id, match.stream)
```

```text
0001_R01-M001 {'twitch': 'daboross', 'youtube': '...'}
...
```

```{note}
`rawstreams` and `streamurls` are accepted on all resources but only meaningful for the `/match`
endpoint. On other resources, they are silently ignored.
```

## Team templates

Team template endpoints have a different API signature from standard resources.

### Single lookup

```python
from liquipydia import TeamTemplate

response = client.team_templates.get("dota2", "teamliquid")

for record in response.result:
    if record is not None:
        template = TeamTemplate.model_validate(record)
        print(template.name, template.shortname)
```

```text
Team Liquid TL
```

Use the `date` parameter for historical logos:

```python
response = client.team_templates.get("dota2", "teamliquid", date="2020-01-01")
```

### Listing all templates

```python
from liquipydia import TeamTemplateList

response = client.team_template_list.list("rocketleague")

for record in response.result:
    if record is not None:
        template = TeamTemplateList.model_validate(record)
        print(template.template, template.name)
```

```text
teamliquid Team Liquid
g2esports G2 Esports
...
```

Use `pagination` for page-based navigation:

```python
# Get page 2
response = client.team_template_list.list("rocketleague", pagination=2)
```

## Error handling

```python
from liquipydia import (
    LiquipediaClient,
    AuthError,
    NotFoundError,
    RateLimitError,
    ApiError,
    LiquipediaError,
)

with LiquipediaClient("my-app", api_key="your-api-key") as client:
    try:
        response = client.players.list("dota2")
    except AuthError:
        print("Invalid or missing API key")
    except NotFoundError:
        print("Requested data does not exist")
    except RateLimitError as e:
        print(f"Rate limited — retry after {e.retry_after}s")
    except ApiError as e:
        print(f"API error: {e.message}")
    except LiquipediaError as e:
        print(f"Unexpected error: {e.message}")
```

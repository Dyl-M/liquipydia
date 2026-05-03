# Examples

All examples below use the recommended context-manager form. The `with` statement guarantees the
underlying HTTP session is closed even if an exception is raised:

```python
from liquipydia import LiquipediaClient

with LiquipediaClient("my-app", api_key="your-api-key") as client:
    ...  # all calls go inside this block
```

For brevity, the `with` block is omitted in the snippets below — assume each example runs inside one.

## Standard resources

13 of the 16 resources share the same `list()` and `paginate()` interface: `broadcasters`,
`companies`, `datapoints`, `external_media_links`, `matches`, `placements`, `players`, `series`,
`squad_players`, `standings_entries`, `standings_tables`, `teams`, `tournaments`, `transfers`.

The examples below use `players` and `tournaments`, but the pattern is identical for the others.

### Basic query

```python
from liquipydia import Player

response = client.players.list("rocketleague", limit=5, order="earnings DESC")

for record in response.result:
    player = Player.model_validate(record)
    print(player.id, player.nationality, player.earnings)
```

The default `limit` is 50. Without an `order`, the API returns records in its own internal order —
add an explicit `order` whenever you care about which records come first.

### Conditions syntax

LPDB conditions use double-bracket delimiters with these operators:

| Syntax              | Meaning      |
|---------------------|--------------|
| `[[col::value]]`    | Equals       |
| `[[col::!value]]`   | Not equals   |
| `[[col::<value]]`   | Less than    |
| `[[col::>value]]`   | Greater than |

Combine with `AND` / `OR` and group with parentheses:

```python
response = client.tournaments.list(
    "dota2",
    conditions="[[liquipediatier::1]] AND ([[type::Online]] OR [[type::Offline]])",
    limit=20,
)
```

JSON subkeys are accessed with an underscore (e.g. `[[extradata_key::value]]`). Date columns
support `YEAR()`, `MONTH()`, `DAY()`, `HOUR()`, `MINUTE()`, `SECOND()` via virtual fields like
`birthdate_year`.

### Keyword filters

Instead of writing condition strings by hand, pass keyword arguments — each becomes one
`[[key::value]]` term, AND-joined automatically:

```python
# Equivalent to conditions="[[pagename::Zen]]"
response = client.players.list("rocketleague", pagename="Zen")
```

The same operator prefixes from the conditions syntax also work in values:

```python
# >, <, ! are passed through verbatim into the condition string
response = client.tournaments.list(
    "dota2",
    liquipediatier="1",         # equals
    prizepool=">100000",        # greater than
    type="!Online",             # not equals
)
```

```{note}
Keyword filter keys are validated against the resource's Pydantic model fields and raise
`ValueError` if unknown. Raw `conditions` strings are *not* validated — the API silently returns
no results for unknown column names.
```

Keyword filters and an explicit `conditions` string can be combined; they are AND-joined:

```python
response = client.players.list(
    "counterstrike",
    conditions="[[status::Active]]",
    nationality="Denmark",
)
```

### Selecting fields

Use `query` to return only specific fields. This reduces payload size on large queries:

```python
response = client.players.list(
    "dota2",
    query="pagename,id,nationality",
    limit=5,
)
for record in response.result:
    print(record["pagename"], record.get("nationality"))
```

```{tip}
`query` also supports aggregate functions (`sum::prizemoney`, `count::id`) and date extractors
(`year::birthdate`). The result field name becomes `sum_prizemoney`, `year_birthdate`, etc.
```

### Ordering and grouping

`order` is SQL-style; use `ASC` / `DESC` and chain with commas:

```python
response = client.tournaments.list(
    "dota2",
    order="startdate DESC, prizepool DESC",
    limit=10,
)
```

`groupby` follows the same syntax and is useful with aggregate `query` functions:

```python
response = client.placements.list(
    "dota2",
    query="sum::prizemoney",
    groupby="opponentname ASC",
    limit=20,
)
```

### Multi-wiki queries

Pipe-separate wiki names to query across multiple games in a single request:

```python
response = client.players.list("dota2|counterstrike", nationality="Denmark", limit=20)
```

Single-wiki endpoints (`team_templates`, `team_template_list`) don't support multi-wiki.

## Pagination

`paginate()` handles offset management automatically and yields individual record dicts:

```python
from liquipydia import Tournament

# Iterate 200 Dota 2 tournaments, 50 per request
tournaments = client.tournaments.paginate(
    "dota2",
    order="startdate DESC",
    page_size=50,
    max_results=200,
)
for record in tournaments:
    tournament = Tournament.model_validate(record)
    print(tournament.name, tournament.startdate)
```

Without `max_results`, pagination continues until a page returns fewer rows than `page_size`:

```python
# Walk every Active Danish CS player — bounded by a filter, not a hard cap
for record in client.players.paginate(
    "counterstrike",
    nationality="Denmark",
    status="Active",
    page_size=100,
):
    player = Player.model_validate(record)
    print(player.id)
```

```{warning}
Always pair an unbounded `paginate()` with restrictive filters or `max_results`. Iterating the
full population of a resource on a large wiki can take many minutes and burn through rate-limit
budget.
```

## Matches (stream data)

The `/match` endpoint accepts two extra parameters that ask the API to include broadcaster stream
metadata in each match record:

```python
from liquipydia import Match

response = client.matches.list(
    "rocketleague",
    rawstreams=True,
    streamurls=True,
    order="date DESC",
    limit=5,
)
for record in response.result:
    match = Match.model_validate(record)
    if match.stream:
        print(match.match2id, match.date, list(match.stream))
```

Both parameters also work with `paginate()`:

```python
for record in client.matches.paginate(
    "dota2",
    rawstreams=True,
    streamurls=True,
    order="date DESC",
    max_results=50,
):
    match = Match.model_validate(record)
```

```{note}
`rawstreams` and `streamurls` are accepted on every resource for API uniformity but only
meaningful on `/match`. On other endpoints they are silently ignored by the API. The library
omits both parameters from the request when they are `False` (the default).
```

## Team templates

Team-template endpoints have a different signature — neither `conditions` nor `limit`/`offset`
applies. Both endpoints occasionally return `None` entries mixed into `response.result`, so always
filter before validating.

### Single template lookup

```python
from liquipydia import TeamTemplate

response = client.team_templates.get("dota2", "teamliquid")

for record in response.result:
    if record is None:
        continue
    template = TeamTemplate.model_validate(record)
    print(template.template, template.name, template.shortname)
```

The optional `date` parameter returns the template state at that point in time — useful when
rendering historical tournament pages with the era-correct logo:

```python
# Team Liquid's logo as it stood on 2020-01-01
response = client.team_templates.get("dota2", "teamliquid", date="2020-01-01")
```

### Listing all templates

```python
from liquipydia import TeamTemplateList

response = client.team_template_list.list("rocketleague")

for record in response.result:
    if record is None:
        continue
    template = TeamTemplateList.model_validate(record)
    print(template.template, template.name)
```

This endpoint uses page-based navigation via the `pagination` parameter (no `limit`/`offset`):

```python
# Get page 2
response = client.team_template_list.list("rocketleague", pagination=2)
```

## Inspecting warnings

`ApiResponse` carries any non-fatal warnings the API emitted alongside the result. They never
raise — check the field if you want to surface them:

```python
response = client.players.list("dota2", limit=5)

if response.warnings:
    for warning in response.warnings:
        print(f"[liquipedia] {warning}")

for record in response.result:
    ...
```

## Error handling

All exceptions inherit from `LiquipediaError`, so catching it alone covers everything. Catch
specific subclasses when you want to react differently per failure mode:

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
    except RateLimitError as exc:
        if exc.retry_after is not None:
            print(f"Rate limited — retry after {exc.retry_after}s")
        else:
            print("Rate limited — no Retry-After hint provided")
    except ApiError as exc:
        print(f"API returned an error: {exc.message}")
    except LiquipediaError as exc:
        print(f"Other library error: {exc.message}")
```

The client retries `429` responses with exponential backoff up to `max_retries` times before
raising `RateLimitError`. If you need to handle rate limits explicitly without retries, set
`max_retries=0` on construction.

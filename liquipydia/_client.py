"""Core HTTP client for the Liquipedia API (LPDB v3)."""

# Standard library
from collections.abc import Iterator
import os
import time
from types import TracebackType
from typing import Any, Final, Self

# Third-party
import httpx

# Local
from liquipydia._exceptions import ApiError, AuthError, LiquipediaError, NotFoundError, RateLimitError
from liquipydia._resources import (
    BroadcastersResource,
    CompaniesResource,
    DatapointsResource,
    ExternalMediaLinksResource,
    MatchResource,
    PlacementsResource,
    PlayersResource,
    SeriesResource,
    SquadPlayersResource,
    StandingsEntriesResource,
    StandingsTablesResource,
    TeamsResource,
    TeamTemplateListResource,
    TeamTemplateResource,
    TournamentsResource,
    TransfersResource,
)
from liquipydia._response import ApiResponse

# === Constants ===

_VERSION: Final[str] = "0.0.4"
_BASE_URL: Final[str] = "https://api.liquipedia.net/api/v3/"
_ENV_API_KEY: Final[str] = "LIQUIPEDIA_API_KEY"
_MAX_BACKOFF: Final[float] = 60.0


# === Client ===


class LiquipediaClient:
    """Synchronous client for the Liquipedia API v3.

    Args:
        app_name: Application name used in the User-Agent header.
        api_key: API key for authentication. Falls back to the LIQUIPEDIA_API_KEY environment variable.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on HTTP 429 responses.
        retry_backoff_factor: Base factor for exponential backoff on retries.

    Examples:
        >>> with LiquipediaClient("my-app", api_key="secret") as client:
        ...     response = client.players.list("dota2")
    """

    # --- Resource attributes ---

    broadcasters: BroadcastersResource
    companies: CompaniesResource
    datapoints: DatapointsResource
    external_media_links: ExternalMediaLinksResource
    matches: MatchResource
    placements: PlacementsResource
    players: PlayersResource
    series: SeriesResource
    squad_players: SquadPlayersResource
    standings_entries: StandingsEntriesResource
    standings_tables: StandingsTablesResource
    teams: TeamsResource
    tournaments: TournamentsResource
    transfers: TransfersResource
    team_templates: TeamTemplateResource
    team_template_list: TeamTemplateListResource

    def __init__(
        self,
        app_name: str,
        api_key: str | None = None,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff_factor: float = 1.0,
    ) -> None:
        self._max_retries = max_retries
        self._retry_backoff_factor = retry_backoff_factor

        resolved_key = api_key or os.environ.get(_ENV_API_KEY)

        headers: dict[str, str] = {
            "User-Agent": f"{app_name} (via liquipydia/{_VERSION})",
            "Accept-Encoding": "gzip",
        }

        if resolved_key:
            headers["Authorization"] = f"Apikey {resolved_key}"

        self._http = httpx.Client(base_url=_BASE_URL, headers=headers, timeout=timeout)

        # --- Resources ---
        self.broadcasters = BroadcastersResource(self)
        self.companies = CompaniesResource(self)
        self.datapoints = DatapointsResource(self)
        self.external_media_links = ExternalMediaLinksResource(self)
        self.matches = MatchResource(self)
        self.placements = PlacementsResource(self)
        self.players = PlayersResource(self)
        self.series = SeriesResource(self)
        self.squad_players = SquadPlayersResource(self)
        self.standings_entries = StandingsEntriesResource(self)
        self.standings_tables = StandingsTablesResource(self)
        self.teams = TeamsResource(self)
        self.tournaments = TournamentsResource(self)
        self.transfers = TransfersResource(self)
        self.team_templates = TeamTemplateResource(self)
        self.team_template_list = TeamTemplateListResource(self)

    # --- Context manager ---

    def __enter__(self) -> Self:
        """Enter the client context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the client context manager and close the HTTP session."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._http.close()

    # --- Request handling ---

    def get(self, endpoint: str, params: dict[str, Any]) -> ApiResponse:
        """Send a GET request to the API and return the parsed response.

        Args:
            endpoint: API path segment (e.g. ``"player"``).
            params: Query parameters to include in the request.

        Returns:
            Parsed API response.

        Raises:
            AuthError: If the API key is invalid or missing (HTTP 403).
            NotFoundError: If the requested data does not exist (HTTP 404).
            RateLimitError: If retries are exhausted after HTTP 429 responses.
            ApiError: If the API returns an error in the response body.
            LiquipediaError: For other unexpected HTTP errors.
        """
        last_retry_after: int | None = None

        for attempt in range(self._max_retries + 1):
            response = self._http.get(endpoint, params=params)

            if response.status_code != 429:
                return self._parse_response(response)

            retry_after = self._get_retry_after(response)
            last_retry_after = retry_after
            backoff = min(self._retry_backoff_factor * (2**attempt), _MAX_BACKOFF)
            sleep_duration: float = retry_after if retry_after > 0 else backoff

            if attempt < self._max_retries:
                time.sleep(sleep_duration)

        raise RateLimitError("Rate limit exceeded after retries", retry_after=last_retry_after)

    @staticmethod
    def _parse_response(response: httpx.Response) -> ApiResponse:
        """Parse an HTTP response into an ApiResponse.

        Args:
            response: The raw httpx response.

        Returns:
            Parsed API response.

        Raises:
            AuthError: On HTTP 403.
            NotFoundError: On HTTP 404.
            LiquipediaError: On other HTTP errors.
            ApiError: When the response body contains an error array.
        """
        if response.status_code == 403:
            raise AuthError("Invalid or missing API key")

        if response.status_code == 404:
            raise NotFoundError("Requested data does not exist")

        if response.status_code >= 400:
            raise LiquipediaError(f"HTTP {response.status_code}: {response.text}")

        body: dict[str, Any] = response.json()

        errors: list[str] = body.get("error", [])
        if errors:
            raise ApiError("; ".join(errors))

        return ApiResponse(
            result=body.get("result", []),
            warnings=body.get("warning", []),
        )

    # --- Pagination ---

    def paginate(
        self,
        endpoint: str,
        params: dict[str, Any],
        *,
        page_size: int = 20,
        max_results: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Iterate through paginated API results.

        Yields individual record dicts, automatically requesting successive pages.
        Stops when a page returns fewer records than ``page_size`` or when
        ``max_results`` records have been yielded.

        Args:
            endpoint: API path segment (e.g. ``"player"``).
            params: Base query parameters (``limit`` and ``offset`` are managed internally).
            page_size: Number of records per page (max 1000).
            max_results: Stop after yielding this many records. None for unlimited.

        Yields:
            Individual record dicts from the API.
        """
        if page_size < 1:
            raise ValueError(f"page_size must be >= 1, got {page_size}")

        offset = 0
        yielded = 0

        while True:
            page_params = params | {"limit": page_size, "offset": offset}
            response = self.get(endpoint, page_params)
            records = response.result

            for record in records:
                yield record
                yielded += 1

                if max_results is not None and yielded >= max_results:
                    return

            if len(records) < page_size:
                return

            offset += page_size

    # --- Helpers ---

    @staticmethod
    def _get_retry_after(response: httpx.Response) -> int:
        """Extract the Retry-After header value from a response.

        Args:
            response: The HTTP response to extract the header from.

        Returns:
            Retry-After value in seconds, or 0 if the header is absent or invalid.
        """
        raw = response.headers.get("Retry-After", "")

        try:
            return int(raw)
        except ValueError:
            return 0

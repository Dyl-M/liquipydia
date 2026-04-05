"""Response wrapper for parsed API envelopes."""

# Standard library
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApiResponse:
    """Parsed response from the Liquipedia API.

    Attributes:
        result: List of record dicts returned by the API.
        warnings: List of warning strings (empty if none).
    """

    result: list[dict[str, Any]]
    warnings: list[str]

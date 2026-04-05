"""Python client library for the Liquipedia API (LPDB v3)."""

# Local
from liquipydia._client import LiquipediaClient  # skipcq: PY-W2000
from liquipydia._exceptions import (  # skipcq: PY-W2000
    ApiError,
    AuthError,
    LiquipediaError,
    NotFoundError,
    RateLimitError,
)
from liquipydia._response import ApiResponse  # skipcq: PY-W2000

__version__ = "0.0.2"
__author__ = "Dylan Monfret"

__all__: list[str] = [
    # Metadata
    "__author__",
    "__version__",
    # Client
    "LiquipediaClient",
    # Response
    "ApiResponse",
    # Exceptions
    "ApiError",
    "AuthError",
    "LiquipediaError",
    "NotFoundError",
    "RateLimitError",
]

"""Python client library for the Liquipedia API (LPDB v3)."""

# Local
from liquipydia._client import LiquipediaClient
from liquipydia._exceptions import ApiError, AuthError, LiquipediaError, NotFoundError, RateLimitError
from liquipydia._response import ApiResponse

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

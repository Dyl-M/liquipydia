"""Python client library for the Liquipedia API (LPDB v3)."""

# Local (explicit re-exports)
from liquipydia._client import LiquipediaClient as LiquipediaClient
from liquipydia._exceptions import ApiError as ApiError
from liquipydia._exceptions import AuthError as AuthError
from liquipydia._exceptions import LiquipediaError as LiquipediaError
from liquipydia._exceptions import NotFoundError as NotFoundError
from liquipydia._exceptions import RateLimitError as RateLimitError
from liquipydia._response import ApiResponse as ApiResponse

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

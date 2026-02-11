"""ENTSO-E Transparency Platform API client library."""

from .client import Client
from .exceptions import ENTSOEError, InvalidParameterError, NoDataError, RateLimitError

__version__ = "0.1.0"
__all__ = [
    "Client",
    "ENTSOEError",
    "InvalidParameterError",
    "NoDataError",
    "RateLimitError",
]

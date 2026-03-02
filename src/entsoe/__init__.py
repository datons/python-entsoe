"""ENTSO-E Transparency Platform API client library."""

from .client import Client, ENTSOEClient
from .exceptions import ENTSOEError, InvalidParameterError, NoDataError, RateLimitError
from ._mappings import COUNTRY_NAMES, PSR_CODES, country_name, psr_name

__version__ = "0.4.2"
__all__ = [
    "Client",
    "COUNTRY_NAMES",
    "ENTSOEClient",
    "ENTSOEError",
    "InvalidParameterError",
    "NoDataError",
    "PSR_CODES",
    "RateLimitError",
    "country_name",
    "psr_name",
]

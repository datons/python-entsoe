"""ENTSO-E Transparency Platform API client library."""

from .client import Client
from .exceptions import ENTSOEError, InvalidParameterError, NoDataError, RateLimitError
from ._mappings import (
    AREAS,
    AREA_CODES,
    BUSINESS_TYPES,
    COUNTRY_NAMES,
    DOC_STATUS,
    DOCUMENT_TYPES,
    MARKET_AGREEMENT_TYPES,
    PRICE_CATEGORIES,
    PROCESS_TYPES,
    PSR_CODES,
    PSR_TYPES,
    country_name,
    psr_name,
)

__version__ = "0.3.1"
__all__ = [
    "AREAS",
    "AREA_CODES",
    "BUSINESS_TYPES",
    "COUNTRY_NAMES",
    "Client",
    "DOC_STATUS",
    "DOCUMENT_TYPES",
    "ENTSOEError",
    "InvalidParameterError",
    "MARKET_AGREEMENT_TYPES",
    "NoDataError",
    "PRICE_CATEGORIES",
    "PROCESS_TYPES",
    "PSR_CODES",
    "PSR_TYPES",
    "RateLimitError",
    "country_name",
    "psr_name",
]

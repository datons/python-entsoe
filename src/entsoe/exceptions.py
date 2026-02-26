"""Exception hierarchy for the ENTSO-E client."""

from __future__ import annotations


class ENTSOEError(Exception):
    """Base exception for all ENTSO-E API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class NoDataError(ENTSOEError):
    """Raised when the API returns no data for the requested period/parameters."""

    def __init__(self, message: str = "No data available for the requested parameters."):
        super().__init__(message)


class InvalidParameterError(ENTSOEError):
    """Raised when invalid parameters are passed (bad country code, naive timestamps, etc.)."""

    def __init__(self, message: str):
        super().__init__(message)


class RateLimitError(ENTSOEError):
    """Raised when rate limit is exceeded and all retries are exhausted."""

    def __init__(self, message: str = "Rate limit exceeded. Retries exhausted."):
        super().__init__(message, status_code=429)

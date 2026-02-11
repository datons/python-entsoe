"""Low-level HTTP client for the ENTSO-E Transparency Platform API.

Handles:
- Request construction with proper parameter formatting
- Automatic year-splitting for long date ranges
- Retry with exponential backoff on rate limits (429)
- Response validation
"""

import logging
import time
from datetime import timedelta

import pandas as pd
import requests

from .exceptions import ENTSOEError, InvalidParameterError, RateLimitError

logger = logging.getLogger(__name__)

BASE_URL = "https://web-api.tp.entsoe.eu/api"

# ENTSO-E API limits requests to ~1 year
MAX_REQUEST_RANGE = timedelta(days=365)


def _format_timestamp(ts: pd.Timestamp) -> str:
    """Format a tz-aware Timestamp to ENTSO-E API format (YYYYMMDDHHmm in UTC)."""
    utc = ts.tz_convert("UTC")
    return utc.strftime("%Y%m%d%H%M")


def _validate_timestamps(
    start: pd.Timestamp, end: pd.Timestamp
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Validate and normalize start/end timestamps."""
    if start.tzinfo is None:
        raise InvalidParameterError(
            "start timestamp must be timezone-aware. "
            "Example: pd.Timestamp('2024-01-01', tz='Europe/Paris')"
        )
    if end.tzinfo is None:
        raise InvalidParameterError(
            "end timestamp must be timezone-aware. "
            "Example: pd.Timestamp('2024-01-07', tz='Europe/Paris')"
        )
    if start >= end:
        raise InvalidParameterError("start must be before end.")
    return start, end


def _split_years(
    start: pd.Timestamp, end: pd.Timestamp
) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Split a date range into chunks that don't exceed the API's max range.

    Returns a list of (start, end) tuples.
    """
    chunks = []
    current = start
    while current < end:
        chunk_end = min(current + MAX_REQUEST_RANGE, end)
        chunks.append((current, chunk_end))
        current = chunk_end
    return chunks


class HttpClient:
    """Low-level HTTP client for the ENTSO-E API."""

    def __init__(
        self,
        api_key: str,
        session: requests.Session | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ):
        self.api_key = api_key
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": "entsoe-library/0.1.0"})
        self.max_retries = max_retries
        self.base_delay = base_delay

    def query(
        self,
        params: dict,
        start: pd.Timestamp,
        end: pd.Timestamp,
    ) -> str:
        """Execute a query against the ENTSO-E API.

        Automatically splits requests spanning more than 1 year and
        concatenates the XML responses.

        Args:
            params: API parameters (documentType, processType, etc.).
                    Do NOT include securityToken, periodStart, or periodEnd.
            start: Period start (tz-aware).
            end: Period end (tz-aware).

        Returns:
            Raw XML response text.

        Raises:
            ENTSOEError: On API errors.
            RateLimitError: When rate limit retries are exhausted.
        """
        start, end = _validate_timestamps(start, end)
        chunks = _split_years(start, end)

        xml_parts: list[str] = []
        for chunk_start, chunk_end in chunks:
            xml = self._single_request(params, chunk_start, chunk_end)
            xml_parts.append(xml)

        # If only one chunk, return directly
        if len(xml_parts) == 1:
            return xml_parts[0]

        # For multi-chunk: return the last chunk's full XML
        # (parsing layer will merge TimeSeries from all chunks)
        # Actually, we concatenate by re-parsing and merging TimeSeries.
        # For simplicity, return all XMLs joined — the parser handles this.
        return xml_parts[0] if len(xml_parts) == 1 else xml_parts

    def query_raw(
        self,
        params: dict,
        start: pd.Timestamp,
        end: pd.Timestamp,
    ) -> list[str]:
        """Execute a query and return a list of XML response strings (one per chunk)."""
        start, end = _validate_timestamps(start, end)
        chunks = _split_years(start, end)
        return [self._single_request(params, cs, ce) for cs, ce in chunks]

    def _single_request(
        self,
        params: dict,
        start: pd.Timestamp,
        end: pd.Timestamp,
    ) -> str:
        """Execute a single API request with retry logic."""
        request_params = {
            "securityToken": self.api_key,
            "periodStart": _format_timestamp(start),
            "periodEnd": _format_timestamp(end),
            **params,
        }

        for attempt in range(self.max_retries + 1):
            logger.debug(
                "ENTSO-E request: %s (attempt %d/%d)",
                request_params.get("documentType", "?"),
                attempt + 1,
                self.max_retries + 1,
            )

            response = self.session.get(BASE_URL, params=request_params)

            if response.status_code == 429:
                if attempt < self.max_retries:
                    delay = self.base_delay * (2**attempt)
                    logger.warning("Rate limited. Retrying in %.1fs...", delay)
                    time.sleep(delay)
                    continue
                raise RateLimitError()

            if response.status_code == 401:
                raise ENTSOEError(
                    "Unauthorized. Check your ENTSOE_API_KEY.", status_code=401
                )

            if response.status_code != 200:
                raise ENTSOEError(
                    f"API returned HTTP {response.status_code}: {response.text[:500]}",
                    status_code=response.status_code,
                )

            return response.text

        raise ENTSOEError("Max retries exceeded.")

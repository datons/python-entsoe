"""Base namespace class shared by all domain namespaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

import pandas as pd

from .._mappings import lookup_area
from .._xml import parse_timeseries

if TYPE_CHECKING:
    from .._http import HttpClient

#: Accepted timestamp types for public namespace methods.
Timestamp = Union[str, pd.Timestamp]


class BaseNamespace:
    """Base class for domain namespaces.

    Holds a reference to the shared HttpClient and provides
    common helper methods for building queries and parsing responses.
    """

    def __init__(self, http: HttpClient, *, tz: str = "Europe/Brussels") -> None:
        self._http = http
        self._tz = tz

    # ------------------------------------------------------------------
    # Timestamp coercion
    # ------------------------------------------------------------------

    def _resolve_ts(self, value: Timestamp) -> pd.Timestamp:
        """Coerce *value* to a tz-aware :class:`pd.Timestamp`.

        * ``str`` → ``pd.Timestamp(value, tz=self._tz)``
        * ``pd.Timestamp`` with tz → returned unchanged
        * ``pd.Timestamp`` without tz → raises (existing behaviour)
        """
        if isinstance(value, str):
            return pd.Timestamp(value, tz=self._tz)
        return value  # pd.Timestamp — _validate_timestamps checks tz later

    def _query(
        self,
        params: dict,
        start: Timestamp,
        end: Timestamp,
    ) -> pd.DataFrame:
        """Execute a query and parse the XML response into a DataFrame."""
        start_ts = self._resolve_ts(start)
        end_ts = self._resolve_ts(end)
        result = self._http.query(params, start_ts, end_ts)

        # Handle multi-chunk responses (year-splitting)
        if isinstance(result, list):
            dfs = [parse_timeseries(xml) for xml in result]
            return pd.concat(dfs, ignore_index=True).sort_values("timestamp").reset_index(drop=True)

        return parse_timeseries(result)

    @staticmethod
    def _area(country: str) -> str:
        """Resolve country code to EIC area code."""
        return lookup_area(country)

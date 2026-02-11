"""Base namespace class shared by all domain namespaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from .._mappings import lookup_area
from .._xml import parse_timeseries

if TYPE_CHECKING:
    from .._http import HttpClient


class BaseNamespace:
    """Base class for domain namespaces.

    Holds a reference to the shared HttpClient and provides
    common helper methods for building queries and parsing responses.
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _query(
        self,
        params: dict,
        start: pd.Timestamp,
        end: pd.Timestamp,
    ) -> pd.DataFrame:
        """Execute a query and parse the XML response into a DataFrame."""
        result = self._http.query(params, start, end)

        # Handle multi-chunk responses (year-splitting)
        if isinstance(result, list):
            dfs = [parse_timeseries(xml) for xml in result]
            return pd.concat(dfs, ignore_index=True).sort_values("timestamp").reset_index(drop=True)

        return parse_timeseries(result)

    @staticmethod
    def _area(country: str) -> str:
        """Resolve country code to EIC area code."""
        return lookup_area(country)

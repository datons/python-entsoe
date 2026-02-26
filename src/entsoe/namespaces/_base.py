"""Base namespace class shared by all domain namespaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union

import pandas as pd

from .._mappings import country_name, lookup_area
from .._xml import parse_timeseries

if TYPE_CHECKING:
    from .._http import HttpClient

#: Accepted timestamp types for public namespace methods.
Timestamp = Union[str, pd.Timestamp]

#: Parameters that accept a single value or a list.
OneOrMany = Union[str, list[str]]


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

    def _query_multi(
        self,
        build_params: Callable[[str], dict],
        values: OneOrMany,
        start: Timestamp,
        end: Timestamp,
        *,
        label_fn: Callable[[str], str] = country_name,
        label_col: str = "country",
    ) -> pd.DataFrame:
        """Execute a query for one or many values, concatenating results.

        When *values* is a single string, delegates to :meth:`_query`
        without adding a label column (backward compatible).

        When *values* is a list, iterates over each value, calls
        *build_params(value)* to construct the query parameters, adds a
        *label_col* column with the result of *label_fn(value)*, and
        concatenates all DataFrames.

        Args:
            build_params: Callable that takes a raw value (e.g. "FR") and
                returns the query parameter dict.
            values: A single value or list of values.
            start: Period start.
            end: Period end.
            label_fn: Callable to produce human-readable labels.
            label_col: Column name for the label.

        Returns:
            DataFrame — single-value queries unchanged, multi-value
            queries with an additional label column.
        """
        if isinstance(values, str):
            return self._query(build_params(values), start, end)

        frames = []
        for val in values:
            df = self._query(build_params(val), start, end)
            df[label_col] = label_fn(val)
            frames.append(df)
        return pd.concat(frames, ignore_index=True)

    @staticmethod
    def _area(country: str) -> str:
        """Resolve country code to EIC area code."""
        return lookup_area(country)

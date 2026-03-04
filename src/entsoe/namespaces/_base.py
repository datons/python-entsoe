"""Base namespace class shared by all domain namespaces."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Union

import pandas as pd

from ..exceptions import InvalidParameterError, NoDataError
from .._mappings import country_name, lookup_area

if TYPE_CHECKING:
    from .._http import HttpClient
    from ..cache import CacheStore

logger = logging.getLogger("entsoe")

#: Accepted timestamp types for public namespace methods.
Timestamp = Union[str, pd.Timestamp]

#: Parameters that accept a single value or a list.
OneOrMany = Union[str, list[str]]


class BaseNamespace:
    """Base class for domain namespaces.

    Holds a reference to the shared HttpClient and provides
    common helper methods for building queries and parsing responses.
    """

    def __init__(
        self,
        http: HttpClient,
        *,
        tz: str = "Europe/Brussels",
        cache: CacheStore | None = None,
    ) -> None:
        self._http = http
        self._tz = tz
        self._cache = cache

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
        from .._xml import parse_timeseries

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

    # ------------------------------------------------------------------
    # Cached query support
    # ------------------------------------------------------------------

    def _query_cached(
        self,
        domain: str,
        topic: str,
        partition: str,
        params: dict,
        start: Timestamp,
        end: Timestamp,
        *,
        pivot_col: str | None = None,
        value_col: str = "value",
    ) -> pd.DataFrame:
        """Execute a query with parquet cache support.

        If cache is disabled, delegates to :meth:`_query`. Otherwise:

        1. Read cached wide-format data for the partition
        2. Find gaps (date ranges not covered by cache)
        3. If no gaps → return cached data (no API call)
        4. For each gap → query API, parse, pivot to wide, merge into cache
        5. Return result in long format (API-compatible)

        Args:
            domain: Cache domain (e.g. "prices", "load", "generation").
            topic: Cache topic (e.g. "day_ahead", "actual").
            partition: Cache partition key (e.g. country code "ES").
            params: API query parameters.
            start: Period start.
            end: Period end.
            pivot_col: Column to pivot on for wide format. None for single-value
                data (stored as "value" column).
            value_col: Name of the value column in long format.
        """
        start_ts = self._resolve_ts(start)
        end_ts = self._resolve_ts(end)

        # Validate timestamps upfront (same checks as HttpClient)
        if start_ts.tzinfo is None:
            raise InvalidParameterError(
                "start timestamp must be timezone-aware. "
                "Example: pd.Timestamp('2024-01-01', tz='Europe/Paris')"
            )
        if end_ts.tzinfo is None:
            raise InvalidParameterError(
                "end timestamp must be timezone-aware. "
                "Example: pd.Timestamp('2024-01-07', tz='Europe/Paris')"
            )
        if start_ts >= end_ts:
            raise InvalidParameterError("start must be before end.")

        if self._cache is None:
            return self._query(params, start_ts, end_ts)

        # 1. Read cached wide data
        cached_wide = self._cache.read(domain, topic, partition, start_ts, end_ts)

        # 2. Find gaps
        gaps = self._cache.find_gaps(cached_wide, start_ts, end_ts)

        if not gaps:
            logger.debug(
                "Cache hit: %s/%s/%s [%s → %s]",
                domain, topic, partition, start_ts, end_ts,
            )
            result = self._from_wide(cached_wide, pivot_col, value_col)
            # Restore metadata columns from cached meta
            if not result.empty:
                meta = self._cache.read_meta(domain, topic, partition) or {}
                for col in self._META_COLS:
                    if col in meta and col not in result.columns:
                        result[col] = meta[col]
            return result

        # 3. Filter out degenerate gaps (start >= end) before fetching
        valid_gaps = []
        for gap in gaps:
            gs = gap.start if gap.start.tz is not None else gap.start.tz_localize("UTC")
            ge = gap.end if gap.end.tz is not None else gap.end.tz_localize("UTC")
            if gs < ge:
                valid_gaps.append(gap)

        if not valid_gaps:
            logger.debug(
                "Cache hit: %s/%s/%s [%s → %s] (degenerate gaps filtered)",
                domain, topic, partition, start_ts, end_ts,
            )
            result = self._from_wide(cached_wide, pivot_col, value_col)
            if not result.empty:
                meta = self._cache.read_meta(domain, topic, partition) or {}
                for col in self._META_COLS:
                    if col in meta and col not in result.columns:
                        result[col] = meta[col]
            return result

        logger.debug(
            "Cache miss: %s/%s/%s — %d gap(s) to fill",
            domain, topic, partition, len(valid_gaps),
        )
        new_wide_frames = []
        gap_meta: dict = {}
        for gap in valid_gaps:
            try:
                raw_df = self._query(params, gap.start, gap.end)
                wide, meta = self._to_wide(raw_df, pivot_col, value_col)
                new_wide_frames.append(wide)
                if meta:
                    gap_meta.update(meta)
            except (InvalidParameterError, NoDataError):
                raise
            except Exception as exc:
                logger.warning("Failed to fetch gap %s→%s: %s", gap.start, gap.end, exc)

        # 4. Merge new data with cache and persist
        if new_wide_frames:
            new_wide = pd.concat(new_wide_frames)
            if not cached_wide.empty:
                merged = new_wide.combine_first(cached_wide).sort_index()
            else:
                merged = new_wide.sort_index()

            # Persist full merged data to cache
            self._cache.write(domain, topic, partition, merged)

            # Persist metadata (currency, units, etc.)
            if gap_meta:
                self._cache.write_meta(domain, topic, partition, gap_meta)

            result_wide = merged
        else:
            result_wide = cached_wide

        # 5. Un-pivot and restore metadata columns
        result = self._from_wide(result_wide, pivot_col, value_col)

        if not result.empty:
            # Restore metadata columns from cache
            meta = gap_meta or (self._cache.read_meta(domain, topic, partition) or {})
            for col in self._META_COLS:
                if col in meta and col not in result.columns:
                    result[col] = meta[col]

        return result

    def _query_multi_cached(
        self,
        domain: str,
        topic: str,
        build_params: Callable[[str], dict],
        values: OneOrMany,
        start: Timestamp,
        end: Timestamp,
        *,
        pivot_col: str | None = None,
        value_col: str = "value",
        label_fn: Callable[[str], str] = country_name,
        label_col: str = "country",
    ) -> pd.DataFrame:
        """Execute a cached query for one or many values.

        Each value is its own cache partition. Multi-value queries add
        a label column, same as :meth:`_query_multi`.
        """
        if self._cache is None:
            return self._query_multi(build_params, values, start, end,
                                     label_fn=label_fn, label_col=label_col)

        if isinstance(values, str):
            return self._query_cached(
                domain, topic, values, build_params(values), start, end,
                pivot_col=pivot_col, value_col=value_col,
            )

        frames = []
        for val in values:
            df = self._query_cached(
                domain, topic, val, build_params(val), start, end,
                pivot_col=pivot_col, value_col=value_col,
            )
            df[label_col] = label_fn(val)
            frames.append(df)
        return pd.concat(frames, ignore_index=True)

    # ------------------------------------------------------------------
    # Wide ↔ Long format conversion
    # ------------------------------------------------------------------

    #: Metadata columns that are constant per query and should be preserved
    #: through the cache but not stored in the wide-format parquet.
    _META_COLS = {"currency", "price_unit", "quantity_unit"}

    @staticmethod
    def _to_wide(
        df: pd.DataFrame,
        pivot_col: str | None = None,
        value_col: str = "value",
    ) -> tuple[pd.DataFrame, dict]:
        """Convert a long-format API response to wide format for caching.

        Args:
            df: Long-format DataFrame with a "timestamp" column.
            pivot_col: Column whose unique values become wide-format columns.
                If None, the result has a single "value" column.
            value_col: Name of the value column.

        Returns:
            Tuple of (wide DataFrame with DatetimeIndex, metadata dict of
            constant columns like currency/price_unit).
        """
        if df.empty:
            return pd.DataFrame(), {}

        # Extract constant metadata columns
        meta = {}
        for col in BaseNamespace._META_COLS:
            if col in df.columns:
                vals = df[col].dropna().unique()
                if len(vals) == 1:
                    meta[col] = str(vals[0])

        if pivot_col and pivot_col in df.columns:
            wide = df.pivot_table(
                index="timestamp",
                columns=pivot_col,
                values=value_col,
                aggfunc="first",
            )
            wide.columns.name = None  # Remove pivot column name from columns
        else:
            wide = df.set_index("timestamp")[[value_col]].copy()
            # Deduplicate timestamps (keep last, as API may return overlapping periods)
            wide = wide[~wide.index.duplicated(keep="last")]

        wide.index.name = "timestamp"
        return wide, meta

    @staticmethod
    def _from_wide(
        df: pd.DataFrame,
        pivot_col: str | None = None,
        value_col: str = "value",
    ) -> pd.DataFrame:
        """Convert wide-format cached data back to long format.

        Args:
            df: Wide-format DataFrame with DatetimeIndex.
            pivot_col: If set, melt columns back into this column name.
            value_col: Name for the value column.

        Returns:
            Long-format DataFrame with "timestamp" and value columns.
        """
        if df.empty:
            return pd.DataFrame()

        if pivot_col and len(df.columns) > 0 and not (len(df.columns) == 1 and df.columns[0] == value_col):
            long = df.reset_index().melt(
                id_vars="timestamp",
                var_name=pivot_col,
                value_name=value_col,
            )
            # Drop NaN values (columns that don't have data for all timestamps)
            long = long.dropna(subset=[value_col])
            long = long.sort_values("timestamp").reset_index(drop=True)
            return long
        else:
            return df.reset_index()

    @staticmethod
    def _area(country: str) -> str:
        """Resolve country code to EIC area code."""
        return lookup_area(country)

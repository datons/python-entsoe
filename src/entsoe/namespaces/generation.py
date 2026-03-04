"""Generation namespace — actual generation, forecasts, and capacity queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, OneOrMany, Timestamp
from .._mappings import lookup_psr, psr_name


class GenerationNamespace(BaseNamespace):
    """Access electricity generation data.

    Methods:
        actual: Actual generation output per type.
        forecast: Day-ahead generation forecast (wind/solar).
        installed_capacity: Installed generation capacity per type.
        per_plant: Actual generation per production unit.
    """

    def _gen_query(
        self,
        doc_type: str,
        process_type: str,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
        psr_type: OneOrMany | None,
        *,
        cache_topic: str,
    ) -> pd.DataFrame:
        """Shared logic for generation queries with country + psr_type multi-support."""

        def _params_for_country(code: str) -> dict:
            params = {
                "documentType": doc_type,
                "processType": process_type,
                "in_Domain": self._area(code),
            }
            if psr_type and isinstance(psr_type, str):
                params["psrType"] = lookup_psr(psr_type)
            return params

        # Determine pivot column based on topic
        pivot_col = "unit_name" if cache_topic == "per_plant" else "psr_type"

        # Handle psr_type list case — need to iterate psr types
        if isinstance(psr_type, list):
            countries = country if isinstance(country, list) else [country]
            frames = []
            for code in countries:
                for psr in psr_type:
                    params = {
                        "documentType": doc_type,
                        "processType": process_type,
                        "in_Domain": self._area(code),
                        "psrType": lookup_psr(psr),
                    }
                    if self._cache is not None:
                        sub_df = self._query_cached(
                            "generation", cache_topic, code, params, start, end,
                            pivot_col=pivot_col,
                        )
                    else:
                        sub_df = self._query(params, start, end)
                    if isinstance(country, list):
                        from .._mappings import country_name
                        sub_df["country"] = country_name(code)
                    frames.append(sub_df)
            return pd.concat(frames, ignore_index=True)

        # Standard case: single or no psr_type filter
        df = self._query_multi_cached(
            "generation", cache_topic, _params_for_country, country, start, end,
            pivot_col=pivot_col,
        )

        # When a single psr_type filter is applied, the cache may return all
        # types from a previously unfiltered query. Filter to the requested type.
        if isinstance(psr_type, str) and pivot_col in df.columns:
            resolved_name = psr_name(psr_type)
            df = df[df[pivot_col] == resolved_name].reset_index(drop=True)

        return df

    def actual(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
        psr_type: OneOrMany | None = None,
    ) -> pd.DataFrame:
        """Query actual generation output per type.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.
            psr_type: PSR type code/name, list of codes/names, or None.
                (e.g., "solar", ["solar", "wind_onshore"], or "B16").
                If None, returns all types.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        return self._gen_query("A75", "A16", start, end, country, psr_type,
                               cache_topic="actual")

    def forecast(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
        psr_type: OneOrMany | None = None,
    ) -> pd.DataFrame:
        """Query day-ahead generation forecast (wind and solar).

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.
            psr_type: PSR type code/name, list of codes/names, or None.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        return self._gen_query("A69", "A01", start, end, country, psr_type,
                               cache_topic="forecast")

    def installed_capacity(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
        psr_type: OneOrMany | None = None,
    ) -> pd.DataFrame:
        """Query installed generation capacity per type.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.
            psr_type: PSR type code/name, list of codes/names, or None.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        return self._gen_query("A68", "A33", start, end, country, psr_type,
                               cache_topic="capacity")

    def per_plant(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
        psr_type: OneOrMany | None = None,
    ) -> pd.DataFrame:
        """Query actual generation per production unit.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.
            psr_type: PSR type code/name, list of codes/names, or None.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type,
            and additional unit identifiers.
        """
        return self._gen_query("A73", "A16", start, end, country, psr_type,
                               cache_topic="per_plant")

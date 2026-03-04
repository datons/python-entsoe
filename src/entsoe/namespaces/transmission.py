"""Transmission namespace — cross-border flow and exchange queries."""

from __future__ import annotations

import logging

import pandas as pd

from ._base import BaseNamespace, OneOrMany, Timestamp
from .._mappings import country_name, parse_borders

logger = logging.getLogger("entsoe")


class TransmissionNamespace(BaseNamespace):
    """Access cross-border transmission data.

    Methods:
        crossborder_flows: Physical cross-border flows between two areas.
        scheduled_exchanges: Scheduled commercial exchanges between two areas.
        net_transfer_capacity: Net transfer capacity between two areas.
    """

    def _transmission_query(
        self,
        doc_type: str,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany | None = None,
        country_to: OneOrMany | None = None,
        borders: OneOrMany | None = None,
        extra_params: dict | None = None,
        *,
        cache_topic: str,
    ) -> pd.DataFrame:
        """Shared logic for transmission queries with multi-value support.

        Accepts either ``country_from``/``country_to`` (original API) or
        ``borders`` (shorthand specs like ``"ES-FR"``, ``"ES-*"``,
        ``"iberian"``).  When multiple pairs are queried, results include
        a ``border`` column with labels like ``"France → Spain"``.

        Raises:
            InvalidParameterError: If neither pair nor borders is provided,
                or if both are provided.
        """
        from ..exceptions import InvalidParameterError

        extra = extra_params or {}

        # Resolve which pairs to query
        if borders is not None:
            if country_from is not None or country_to is not None:
                raise InvalidParameterError(
                    "Cannot combine 'borders' with 'country_from'/'country_to'. "
                    "Use one or the other."
                )
            pairs = parse_borders(borders)
            if not pairs:
                raise InvalidParameterError("No border pairs resolved from the given spec.")
        else:
            if country_from is None or country_to is None:
                raise InvalidParameterError(
                    "Provide country_from and country_to, or use borders= "
                    "(e.g. borders='ES-*' or borders='iberian')."
                )
            is_multi_from = isinstance(country_from, list)
            is_multi_to = isinstance(country_to, list)

            if not is_multi_from and not is_multi_to:
                # Single pair — no label column (backward compatible)
                params = {
                    "documentType": doc_type,
                    "in_Domain": self._area(country_to),
                    "out_Domain": self._area(country_from),
                    **extra,
                }
                return self._query_single_border(
                    cache_topic, country_from, country_to, params, start, end,
                )

            froms = country_from if is_multi_from else [country_from]
            tos = country_to if is_multi_to else [country_to]
            pairs = [(cf, ct) for cf in froms for ct in tos]

        # Multiple pairs — iterate and label
        if len(pairs) == 1:
            cf, ct = pairs[0]
            params = {
                "documentType": doc_type,
                "in_Domain": self._area(ct),
                "out_Domain": self._area(cf),
                **extra,
            }
            return self._query_single_border(
                cache_topic, cf, ct, params, start, end,
            )

        frames = []
        for cf, ct in pairs:
            params = {
                "documentType": doc_type,
                "in_Domain": self._area(ct),
                "out_Domain": self._area(cf),
                **extra,
            }
            df = self._query_single_border(
                cache_topic, cf, ct, params, start, end,
            )
            df["border"] = f"{country_name(cf)} → {country_name(ct)}"
            frames.append(df)
        return pd.concat(frames, ignore_index=True)

    def _query_single_border(
        self,
        cache_topic: str,
        country_from: str,
        country_to: str,
        params: dict,
        start: Timestamp,
        end: Timestamp,
    ) -> pd.DataFrame:
        """Query a single border pair, using cache if available.

        Partition is the source country (country_from), and the destination
        country (country_to) is used as the pivot column via ``in_domain``.
        """
        if self._cache is not None:
            return self._query_cached(
                "transmission", cache_topic, country_from, params, start, end,
                pivot_col="in_domain",
            )
        return self._query(params, start, end)

    def crossborder_flows(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany | None = None,
        country_to: OneOrMany | None = None,
        borders: OneOrMany | None = None,
    ) -> pd.DataFrame:
        """Query physical cross-border flows.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code or list of codes.
            country_to: Importing country code or list of codes.
                When either is a list, results include a ``border`` column.
            borders: Border spec or list of specs. Supports ``"ES-FR"``,
                ``"ES-*"`` (all neighbours), ``"iberian"`` (named group),
                and comma-separated combinations like ``"ES-*,FR-*"``.
                Cannot be combined with country_from/country_to.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        return self._transmission_query(
            "A11", start, end, country_from, country_to, borders,
            cache_topic="crossborder_flows",
        )

    def scheduled_exchanges(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany | None = None,
        country_to: OneOrMany | None = None,
        borders: OneOrMany | None = None,
    ) -> pd.DataFrame:
        """Query scheduled commercial exchanges (day-ahead).

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code or list of codes.
            country_to: Importing country code or list of codes.
                When either is a list, results include a ``border`` column.
            borders: Border spec or list of specs. See :meth:`crossborder_flows`.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        return self._transmission_query(
            "A09", start, end, country_from, country_to, borders,
            cache_topic="scheduled_exchanges",
        )

    def net_transfer_capacity(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany | None = None,
        country_to: OneOrMany | None = None,
        borders: OneOrMany | None = None,
    ) -> pd.DataFrame:
        """Query day-ahead net transfer capacity.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code or list of codes.
            country_to: Importing country code or list of codes.
                When either is a list, results include a ``border`` column.
            borders: Border spec or list of specs. See :meth:`crossborder_flows`.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        return self._transmission_query(
            "A61", start, end, country_from, country_to, borders,
            extra_params={"contract_MarketAgreement.Type": "A01"},
            cache_topic="net_transfer_capacity",
        )

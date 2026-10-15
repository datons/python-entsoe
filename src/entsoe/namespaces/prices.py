"""Prices namespace — day-ahead price queries."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pandas as pd

from .._xml import timeseries_contract_type, timeseries_sequence
from ._base import BaseNamespace, OneOrMany, Timestamp

class PricesNamespace(BaseNamespace):
    """Access electricity price data.

    Methods:
        day_ahead: Day-ahead market prices.
    """

    def day_ahead(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
        sequence: int = 1,
    ) -> pd.DataFrame:
        """Query day-ahead electricity prices.

        The A44 document mixes several auctions. Only daily contracts are
        kept (intraday auctions such as the Spanish IDAs are dropped), and
        among them the one with the requested classification sequence.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.
            sequence: Which day-ahead auction to return. ``1`` (default) is
                the Single Day-Ahead Coupling (SDAC, gate closure 12:00 CET).
                ``2`` is the separate EXAA auction (10:15 CET) published for
                DE_LU and AT. Zones that publish a single auction without a
                sequence count as ``1``.

        Returns:
            DataFrame with columns: timestamp, value (EUR/MWh).
            Multi-country queries add a ``country`` column.
        """

        def _params(code: str) -> dict:
            area = self._area(code)
            return {
                "documentType": "A44",
                "in_Domain": area,
                "out_Domain": area,
            }

        def _keep(ts: ET.Element) -> bool:
            if timeseries_contract_type(ts) not in (None, "A01"):
                return False
            return (timeseries_sequence(ts) or 1) == sequence

        return self._query_multi_cached(
            "prices", "day_ahead", _params, country, start, end,
            ts_filter=_keep,
            partition_fn=lambda code: code if sequence == 1 else f"{code}.seq{sequence}",
        )

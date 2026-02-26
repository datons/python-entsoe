"""Prices namespace — day-ahead price queries."""

from __future__ import annotations

import pandas as pd

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
    ) -> pd.DataFrame:
        """Query day-ahead electricity prices.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.

        Returns:
            DataFrame with columns: timestamp, value (EUR/MWh),
            currency, price_unit. Multi-country queries add a ``country`` column.
        """

        def _params(code: str) -> dict:
            area = self._area(code)
            return {
                "documentType": "A44",
                "in_Domain": area,
                "out_Domain": area,
            }

        return self._query_multi(_params, country, start, end)

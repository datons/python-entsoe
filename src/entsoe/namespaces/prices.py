"""Prices namespace — day-ahead price queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, Timestamp


class PricesNamespace(BaseNamespace):
    """Access electricity price data.

    Methods:
        day_ahead: Day-ahead market prices.
    """

    def day_ahead(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
    ) -> pd.DataFrame:
        """Query day-ahead electricity prices.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code (e.g., "FR", "DE").

        Returns:
            DataFrame with columns: timestamp, value (EUR/MWh),
            currency, price_unit.
        """
        area = self._area(country)
        params = {
            "documentType": "A44",
            "in_Domain": area,
            "out_Domain": area,
        }
        return self._query(params, start, end)

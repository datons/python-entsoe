"""Balancing namespace — imbalance price and volume queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, Timestamp


class BalancingNamespace(BaseNamespace):
    """Access balancing market data.

    Methods:
        imbalance_prices: System imbalance prices.
        imbalance_volumes: System imbalance volumes.
    """

    def imbalance_prices(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
    ) -> pd.DataFrame:
        """Query imbalance prices.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code (e.g., "FR", "DE").

        Returns:
            DataFrame with columns: timestamp, value (EUR/MWh).
        """
        area = self._area(country)
        params = {
            "documentType": "A85",
            "controlArea_Domain": area,
        }
        return self._query(params, start, end)

    def imbalance_volumes(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
    ) -> pd.DataFrame:
        """Query imbalance volumes.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code (e.g., "FR", "DE").

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        area = self._area(country)
        params = {
            "documentType": "A86",
            "controlArea_Domain": area,
        }
        return self._query(params, start, end)

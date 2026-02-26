"""Balancing namespace — imbalance price and volume queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, OneOrMany, Timestamp


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
        country: OneOrMany,
    ) -> pd.DataFrame:
        """Query imbalance prices.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "NL"]).
                When a list is passed, results include a ``country`` column.

        Returns:
            DataFrame with columns: timestamp, value (EUR/MWh).
        """

        def _params(code: str) -> dict:
            return {
                "documentType": "A85",
                "controlArea_Domain": self._area(code),
            }

        return self._query_multi(_params, country, start, end)

    def imbalance_volumes(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
    ) -> pd.DataFrame:
        """Query imbalance volumes.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "NL"]).
                When a list is passed, results include a ``country`` column.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """

        def _params(code: str) -> dict:
            return {
                "documentType": "A86",
                "controlArea_Domain": self._area(code),
            }

        return self._query_multi(_params, country, start, end)

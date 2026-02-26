"""Load namespace — actual load and load forecast queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, OneOrMany, Timestamp


class LoadNamespace(BaseNamespace):
    """Access electricity load data.

    Methods:
        actual: Actual total system load.
        forecast: Day-ahead load forecast.
    """

    def actual(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
    ) -> pd.DataFrame:
        """Query actual total system load.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """

        def _params(code: str) -> dict:
            return {
                "documentType": "A65",
                "processType": "A16",
                "outBiddingZone_Domain": self._area(code),
            }

        return self._query_multi(_params, country, start, end)

    def forecast(
        self,
        start: Timestamp,
        end: Timestamp,
        country: OneOrMany,
    ) -> pd.DataFrame:
        """Query day-ahead load forecast.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or list of codes (e.g., "FR" or ["FR", "ES"]).
                When a list is passed, results include a ``country`` column.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """

        def _params(code: str) -> dict:
            return {
                "documentType": "A65",
                "processType": "A01",
                "outBiddingZone_Domain": self._area(code),
            }

        return self._query_multi(_params, country, start, end)

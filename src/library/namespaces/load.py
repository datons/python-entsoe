"""Load namespace — actual load and load forecast queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace


class LoadNamespace(BaseNamespace):
    """Access electricity load data.

    Methods:
        actual: Actual total system load.
        forecast: Day-ahead load forecast.
    """

    def actual(
        self,
        start: pd.Timestamp,
        end: pd.Timestamp,
        country: str,
    ) -> pd.DataFrame:
        """Query actual total system load.

        Args:
            start: Period start (tz-aware).
            end: Period end (tz-aware).
            country: Country code (e.g., "FR", "DE").

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        params = {
            "documentType": "A65",
            "processType": "A16",
            "outBiddingZone_Domain": self._area(country),
        }
        return self._query(params, start, end)

    def forecast(
        self,
        start: pd.Timestamp,
        end: pd.Timestamp,
        country: str,
    ) -> pd.DataFrame:
        """Query day-ahead load forecast.

        Args:
            start: Period start (tz-aware).
            end: Period end (tz-aware).
            country: Country code (e.g., "FR", "DE").

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        params = {
            "documentType": "A65",
            "processType": "A01",
            "outBiddingZone_Domain": self._area(country),
        }
        return self._query(params, start, end)

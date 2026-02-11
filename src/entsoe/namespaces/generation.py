"""Generation namespace — actual generation, forecasts, and capacity queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace


class GenerationNamespace(BaseNamespace):
    """Access electricity generation data.

    Methods:
        actual: Actual generation output per type.
        forecast: Day-ahead generation forecast (wind/solar).
        installed_capacity: Installed generation capacity per type.
        per_plant: Actual generation per production unit.
    """

    def actual(
        self,
        start: pd.Timestamp,
        end: pd.Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query actual generation output per type.

        Args:
            start: Period start (tz-aware).
            end: Period end (tz-aware).
            country: Country code (e.g., "FR", "DE").
            psr_type: Optional PSR type code (e.g., "B16" for Solar,
                      "B19" for Wind Onshore). If None, returns all types.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        params = {
            "documentType": "A75",
            "processType": "A16",
            "in_Domain": self._area(country),
        }
        if psr_type:
            params["psrType"] = psr_type
        return self._query(params, start, end)

    def forecast(
        self,
        start: pd.Timestamp,
        end: pd.Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query day-ahead generation forecast (wind and solar).

        Args:
            start: Period start (tz-aware).
            end: Period end (tz-aware).
            country: Country code (e.g., "FR", "DE").
            psr_type: Optional PSR type code to filter by.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        params = {
            "documentType": "A69",
            "processType": "A01",
            "in_Domain": self._area(country),
        }
        if psr_type:
            params["psrType"] = psr_type
        return self._query(params, start, end)

    def installed_capacity(
        self,
        start: pd.Timestamp,
        end: pd.Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query installed generation capacity per type.

        Args:
            start: Period start (tz-aware).
            end: Period end (tz-aware).
            country: Country code (e.g., "FR", "DE").
            psr_type: Optional PSR type code to filter by.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        params = {
            "documentType": "A68",
            "processType": "A33",
            "in_Domain": self._area(country),
        }
        if psr_type:
            params["psrType"] = psr_type
        return self._query(params, start, end)

    def per_plant(
        self,
        start: pd.Timestamp,
        end: pd.Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query actual generation per production unit.

        Args:
            start: Period start (tz-aware).
            end: Period end (tz-aware).
            country: Country code (e.g., "FR", "DE").
            psr_type: Optional PSR type code to filter by.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type,
            and additional unit identifiers.
        """
        params = {
            "documentType": "A73",
            "processType": "A16",
            "in_Domain": self._area(country),
        }
        if psr_type:
            params["psrType"] = psr_type
        return self._query(params, start, end)

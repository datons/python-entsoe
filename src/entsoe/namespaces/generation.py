"""Generation namespace — actual generation, forecasts, and capacity queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, Timestamp
from .._mappings import lookup_psr


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
        start: Timestamp,
        end: Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query actual generation output per type.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or name (e.g., "FR", "France").
            psr_type: PSR type code or name (e.g., "B16" or "Solar").
                      If None, returns all types.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        params = {
            "documentType": "A75",
            "processType": "A16",
            "in_Domain": self._area(country),
        }
        if psr_type:
            params["psrType"] = lookup_psr(psr_type)
        return self._query(params, start, end)

    def forecast(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query day-ahead generation forecast (wind and solar).

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or name (e.g., "FR", "France").
            psr_type: PSR type code or name to filter by.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        params = {
            "documentType": "A69",
            "processType": "A01",
            "in_Domain": self._area(country),
        }
        if psr_type:
            params["psrType"] = lookup_psr(psr_type)
        return self._query(params, start, end)

    def installed_capacity(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query installed generation capacity per type.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or name (e.g., "FR", "France").
            psr_type: PSR type code or name to filter by.

        Returns:
            DataFrame with columns: timestamp, value (MW), psr_type.
        """
        params = {
            "documentType": "A68",
            "processType": "A33",
            "in_Domain": self._area(country),
        }
        if psr_type:
            params["psrType"] = lookup_psr(psr_type)
        return self._query(params, start, end)

    def per_plant(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
        psr_type: str | None = None,
    ) -> pd.DataFrame:
        """Query actual generation per production unit.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code or name (e.g., "FR", "France").
            psr_type: PSR type code or name to filter by.

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
            params["psrType"] = lookup_psr(psr_type)
        return self._query(params, start, end)

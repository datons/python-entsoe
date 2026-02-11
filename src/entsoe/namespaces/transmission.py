"""Transmission namespace — cross-border flow and exchange queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, Timestamp


class TransmissionNamespace(BaseNamespace):
    """Access cross-border transmission data.

    Methods:
        crossborder_flows: Physical cross-border flows between two areas.
        scheduled_exchanges: Scheduled commercial exchanges between two areas.
        net_transfer_capacity: Net transfer capacity between two areas.
    """

    def crossborder_flows(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: str,
        country_to: str,
    ) -> pd.DataFrame:
        """Query physical cross-border flows.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code (e.g., "FR").
            country_to: Importing country code (e.g., "DE").

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        params = {
            "documentType": "A11",
            "in_Domain": self._area(country_to),
            "out_Domain": self._area(country_from),
        }
        return self._query(params, start, end)

    def scheduled_exchanges(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: str,
        country_to: str,
    ) -> pd.DataFrame:
        """Query scheduled commercial exchanges (day-ahead).

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code (e.g., "FR").
            country_to: Importing country code (e.g., "DE").

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        params = {
            "documentType": "A09",
            "in_Domain": self._area(country_to),
            "out_Domain": self._area(country_from),
        }
        return self._query(params, start, end)

    def net_transfer_capacity(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: str,
        country_to: str,
    ) -> pd.DataFrame:
        """Query day-ahead net transfer capacity.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code (e.g., "FR").
            country_to: Importing country code (e.g., "DE").

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        params = {
            "documentType": "A61",
            "contract_MarketAgreement.Type": "A01",
            "in_Domain": self._area(country_to),
            "out_Domain": self._area(country_from),
        }
        return self._query(params, start, end)

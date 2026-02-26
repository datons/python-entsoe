"""Transmission namespace — cross-border flow and exchange queries."""

from __future__ import annotations

import pandas as pd

from ._base import BaseNamespace, OneOrMany, Timestamp
from .._mappings import country_name


class TransmissionNamespace(BaseNamespace):
    """Access cross-border transmission data.

    Methods:
        crossborder_flows: Physical cross-border flows between two areas.
        scheduled_exchanges: Scheduled commercial exchanges between two areas.
        net_transfer_capacity: Net transfer capacity between two areas.
    """

    def _transmission_query(
        self,
        doc_type: str,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany,
        country_to: OneOrMany,
        extra_params: dict | None = None,
    ) -> pd.DataFrame:
        """Shared logic for transmission queries with multi-value support.

        Supports lists for both country_from and country_to. When either
        is a list, results include a ``border`` column with labels like
        "France → Spain".
        """
        extra = extra_params or {}
        is_multi_from = isinstance(country_from, list)
        is_multi_to = isinstance(country_to, list)

        if not is_multi_from and not is_multi_to:
            # Single pair — no label column
            params = {
                "documentType": doc_type,
                "in_Domain": self._area(country_to),
                "out_Domain": self._area(country_from),
                **extra,
            }
            return self._query(params, start, end)

        # At least one side is a list — iterate and label
        froms = country_from if is_multi_from else [country_from]
        tos = country_to if is_multi_to else [country_to]

        frames = []
        for cf in froms:
            for ct in tos:
                params = {
                    "documentType": doc_type,
                    "in_Domain": self._area(ct),
                    "out_Domain": self._area(cf),
                    **extra,
                }
                df = self._query(params, start, end)
                df["border"] = f"{country_name(cf)} → {country_name(ct)}"
                frames.append(df)
        return pd.concat(frames, ignore_index=True)

    def crossborder_flows(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany,
        country_to: OneOrMany,
    ) -> pd.DataFrame:
        """Query physical cross-border flows.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code or list of codes.
            country_to: Importing country code or list of codes.
                When either is a list, results include a ``border`` column.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        return self._transmission_query("A11", start, end, country_from, country_to)

    def scheduled_exchanges(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany,
        country_to: OneOrMany,
    ) -> pd.DataFrame:
        """Query scheduled commercial exchanges (day-ahead).

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code or list of codes.
            country_to: Importing country code or list of codes.
                When either is a list, results include a ``border`` column.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        return self._transmission_query("A09", start, end, country_from, country_to)

    def net_transfer_capacity(
        self,
        start: Timestamp,
        end: Timestamp,
        country_from: OneOrMany,
        country_to: OneOrMany,
    ) -> pd.DataFrame:
        """Query day-ahead net transfer capacity.

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country_from: Exporting country code or list of codes.
            country_to: Importing country code or list of codes.
                When either is a list, results include a ``border`` column.

        Returns:
            DataFrame with columns: timestamp, value (MW).
        """
        return self._transmission_query(
            "A61", start, end, country_from, country_to,
            extra_params={"contract_MarketAgreement.Type": "A01"},
        )

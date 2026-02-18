"""Balancing namespace — imbalance, reserve, and activation queries."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from ._base import BaseNamespace, Timestamp

# Process type codes for reserve types
_RESERVE_PROCESS_TYPES = {
    "fcr": "A52",   # Frequency Containment Reserve
    "afrr": "A51",  # Automatic Frequency Restoration Reserve
    "mfrr": "A47",  # Manual Frequency Restoration Reserve
}

# Business type codes for activation filtering
_ACTIVATION_BUSINESS_TYPES = {
    "afrr": "A96",
    "mfrr": "A97",
}

# Display names for reserve types
_RESERVE_DISPLAY_NAMES = {
    "fcr": "FCR",
    "afrr": "aFRR",
    "mfrr": "mFRR",
}

ReserveType = Literal["fcr", "afrr", "mfrr"]
ActivationType = Literal["afrr", "mfrr"]


class BalancingNamespace(BaseNamespace):
    """Access balancing market data.

    Methods:
        imbalance_prices: System imbalance prices.
        imbalance_volumes: System imbalance volumes.
        contracted_reserve_prices: Procured reserve capacity prices (FCR/aFRR/mFRR).
        activation_prices: Activated balancing energy prices (aFRR/mFRR).
    """

    # ── Imbalance ────────────────────────────────────────────────────────

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
            DataFrame with columns:
            - timestamp: tz-aware UTC datetime
            - value: Price in EUR/MWh
            - price_category: Price direction ("Long", "Short")
            - currency, price_unit: Metadata columns
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

    # ── Contracted reserves (FCR / aFRR / mFRR) ─────────────────────────

    def contracted_reserve_prices(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
        reserve_type: ReserveType = "fcr",
        market_agreement: str = "A01",
    ) -> pd.DataFrame:
        """Query procured reserve capacity prices.

        Returns the prices for contracted balancing reserves
        (documentType A81 + businessType B95).

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code (e.g., "NL", "DE").
            reserve_type: ``"fcr"``, ``"afrr"``, or ``"mfrr"``.
            market_agreement: Market agreement type code.
                ``"A01"`` = daily (default), ``"A07"`` = weekly.

        Returns:
            DataFrame with columns: timestamp, value (EUR/MW),
            currency, quantity_unit.

        Example::

            df = client.balancing.contracted_reserve_prices(
                "2024-06-01", "2024-06-08", country="NL", reserve_type="fcr"
            )

        Note:
            Data availability varies by TSO. NL has good coverage;
            DE may return NoDataError for some reserve types.
        """
        area = self._area(country)
        process_type = _RESERVE_PROCESS_TYPES[reserve_type]
        params = {
            "documentType": "A81",
            "businessType": "B95",
            "processType": process_type,
            "controlArea_Domain": area,
            "type_MarketAgreement.Type": market_agreement,
        }
        df = self._query(params, start, end)
        df["reserve_type"] = _RESERVE_DISPLAY_NAMES[reserve_type]
        return df

    # ── Activated balancing energy prices ─────────────────────────────────

    def activation_prices(
        self,
        start: Timestamp,
        end: Timestamp,
        country: str,
        reserve_type: ActivationType | None = None,
    ) -> pd.DataFrame:
        """Query activated balancing energy prices.

        Returns the prices of activated balancing energy
        (documentType A84, processType A16 = realised).

        Args:
            start: Period start — date string or tz-aware Timestamp.
            end: Period end — date string or tz-aware Timestamp.
            country: Country code (e.g., "NL", "DE").
            reserve_type: Optional filter — ``"afrr"`` or ``"mfrr"``.
                If ``None``, returns all activation prices.

        Returns:
            DataFrame with columns: timestamp, value (EUR/MWh),
            currency, price_unit.

        Example::

            # All activation prices
            df = client.balancing.activation_prices(
                "2024-06-01", "2024-06-08", country="NL"
            )

            # aFRR only
            df = client.balancing.activation_prices(
                "2024-06-01", "2024-06-08", country="NL", reserve_type="afrr"
            )
        """
        area = self._area(country)
        params = {
            "documentType": "A84",
            "processType": "A16",
            "controlArea_Domain": area,
        }
        if reserve_type is not None:
            params["businessType"] = _ACTIVATION_BUSINESS_TYPES[reserve_type]
        df = self._query(params, start, end)
        if reserve_type is not None:
            df["reserve_type"] = _RESERVE_DISPLAY_NAMES[reserve_type]
        return df

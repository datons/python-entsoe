"""Tests for the balancing namespace."""

import pandas as pd
import pytest

from entsoe import Client


class TestImbalancePrices:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.balancing.imbalance_prices(start, end, country="FR")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_required_columns(self, client: Client, short_range):
        start, end = short_range
        df = client.balancing.imbalance_prices(start, end, country="FR")
        assert "timestamp" in df.columns
        assert "value" in df.columns

    def test_values_are_numeric(self, client: Client, short_range):
        start, end = short_range
        df = client.balancing.imbalance_prices(start, end, country="FR")
        assert pd.api.types.is_numeric_dtype(df["value"])

    def test_has_category_column(self, client: Client, short_range):
        """Verify imbalance_price_category column is present to differentiate duplicate timestamps."""
        start, end = short_range
        df = client.balancing.imbalance_prices(start, end, country="FR")
        assert "imbalance_price_category" in df.columns
        assert len(df["imbalance_price_category"].unique()) > 0
        # Typically has both A04 and A05 (up and down regulation)
        assert df["imbalance_price_category"].notna().any()

    def test_belgium(self, client: Client, short_range):
        start, end = short_range
        df = client.balancing.imbalance_prices(start, end, country="BE")
        assert len(df) > 0

    def test_netherlands(self, client: Client, short_range):
        start, end = short_range
        df = client.balancing.imbalance_prices(start, end, country="NL")
        assert len(df) > 0

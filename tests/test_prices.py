"""Tests for the prices namespace."""

import pandas as pd
import pytest

from entsoe import Client


class TestDayAheadPrices:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country="FR")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_price_columns(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country="FR")
        assert "timestamp" in df.columns
        assert "value" in df.columns
        assert "currency" in df.columns

    def test_currency_is_eur(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country="FR")
        assert (df["currency"] == "EUR").all()

    def test_germany_uses_de_lu(self, client: Client, short_range):
        """DE alone may not have prices — DE_LU is the correct bidding zone."""
        start, end = short_range
        df = client.prices.day_ahead(start, end, country="DE_LU")
        assert len(df) > 0

    def test_spain(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country="ES")
        assert len(df) > 0

    def test_netherlands(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country="NL")
        assert len(df) > 0

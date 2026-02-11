"""Tests for the load namespace."""

import pandas as pd
import pytest

from entsoe import Client


class TestLoadActual:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.load.actual(start, end, country="FR")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_required_columns(self, client: Client, short_range):
        start, end = short_range
        df = client.load.actual(start, end, country="FR")
        assert "timestamp" in df.columns
        assert "value" in df.columns

    def test_values_are_numeric(self, client: Client, short_range):
        start, end = short_range
        df = client.load.actual(start, end, country="FR")
        assert pd.api.types.is_numeric_dtype(df["value"])

    def test_timestamps_are_utc(self, client: Client, short_range):
        start, end = short_range
        df = client.load.actual(start, end, country="FR")
        assert df["timestamp"].dt.tz is not None

    def test_different_country(self, client: Client, short_range):
        start, end = short_range
        df = client.load.actual(start, end, country="ES")
        assert len(df) > 0


class TestLoadForecast:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.load.forecast(start, end, country="FR")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_required_columns(self, client: Client, short_range):
        start, end = short_range
        df = client.load.forecast(start, end, country="FR")
        assert "timestamp" in df.columns
        assert "value" in df.columns
